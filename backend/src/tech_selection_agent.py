"""Technology selection workflow for AI application stacks."""

from __future__ import annotations

import json
import re
from typing import Any, Iterator

from hello_agents import HelloAgentsLLM

from config import Configuration
from models import (
    CandidateEvaluation,
    DecisionContext,
    DecisionState,
)
from services.candidate_discovery import discover_candidates
from services.dimension_planner import plan_dimensions
from services.exporter import export_markdown_report
from services.matrix_builder import build_comparison_matrix
from services.search import dispatch_search, prepare_research_context
from utils import strip_thinking_tokens


RATING_PATTERN = re.compile(r"(高|中高|中|中低|低)")


class TechSelectionAgent:
    """Orchestrates candidate discovery, evaluation, matrix, and report output."""

    def __init__(self, config: Configuration | None = None) -> None:
        self.config = config or Configuration.from_env()
        self.llm = self._init_llm()

    def _init_llm(self) -> HelloAgentsLLM:
        kwargs: dict[str, Any] = {"temperature": 0.0}
        model_id = self.config.llm_model_id or self.config.local_llm
        if model_id:
            kwargs["model"] = model_id

        provider = (self.config.llm_provider or "").strip()
        if provider:
            kwargs["provider"] = provider

        if provider == "ollama":
            kwargs["base_url"] = self.config.sanitized_ollama_url()
            kwargs["api_key"] = self.config.llm_api_key or "ollama"
        elif provider == "lmstudio":
            kwargs["base_url"] = self.config.lmstudio_base_url
            if self.config.llm_api_key:
                kwargs["api_key"] = self.config.llm_api_key
        else:
            if self.config.llm_base_url:
                kwargs["base_url"] = self.config.llm_base_url
            if self.config.llm_api_key:
                kwargs["api_key"] = self.config.llm_api_key

        return HelloAgentsLLM(**kwargs)

    def run_stream(self, context: DecisionContext) -> Iterator[dict[str, Any]]:
        """Execute the technology selection workflow as SSE-friendly events."""

        state = DecisionState(context=context)
        yield {"type": "status", "message": "初始化 AI 应用技术选型流程"}

        state.candidates = discover_candidates(context)
        yield {
            "type": "candidates_ready",
            "candidates": [candidate.__dict__ for candidate in state.candidates],
        }

        state.dimensions = plan_dimensions(context)
        yield {
            "type": "dimensions_ready",
            "dimensions": [dimension.__dict__ for dimension in state.dimensions],
        }

        for dimension in state.dimensions:
            yield {
                "type": "status",
                "message": f"正在评估维度：{dimension.name}",
                "dimension": dimension.name,
            }
            for candidate in state.candidates:
                query = self._build_query(context, candidate.name, dimension.name, dimension.query_focus)
                search_result, notices, answer_text, backend = dispatch_search(
                    query,
                    self.config,
                    len(state.evaluations),
                )
                sources_summary, source_context = prepare_research_context(
                    search_result,
                    answer_text,
                    self.config,
                )
                for reference in self._extract_references(search_result):
                    if reference not in state.references:
                        state.references.append(reference)

                evaluation = self._evaluate_candidate(
                    context=context,
                    candidate_name=candidate.name,
                    dimension_name=dimension.name,
                    dimension_description=dimension.description,
                    source_context=source_context,
                    sources_summary=sources_summary,
                )
                state.evaluations.append(evaluation)

                yield {
                    "type": "candidate_evaluation",
                    "candidate": candidate.name,
                    "dimension": dimension.name,
                    "evaluation": evaluation.__dict__,
                    "sources_summary": sources_summary,
                    "backend": backend,
                    "notices": notices,
                }

        state.comparison_matrix = build_comparison_matrix(
            state.candidates,
            state.dimensions,
            state.evaluations,
        )
        yield {"type": "comparison_matrix_ready", "matrix": state.comparison_matrix}

        state.report_markdown = self._generate_report(state)
        export_path = export_markdown_report(
            state.report_markdown,
            context.decision_topic,
            self.config.notes_workspace or "./notes",
        )
        yield {
            "type": "decision_report_ready",
            "report": state.report_markdown,
            "matrix": state.comparison_matrix,
            "references": state.references,
            "export_path": export_path,
        }
        yield {
            "type": "final_report",
            "report": state.report_markdown,
            "export_path": export_path,
        }
        yield {"type": "done"}

    def _build_query(
        self,
        context: DecisionContext,
        candidate_name: str,
        dimension_name: str,
        query_focus: str,
    ) -> str:
        constraints = " ".join(
            item
            for item in [
                context.project_type,
                context.deployment_mode,
                context.preferred_language,
                " ".join(context.requirements),
            ]
            if item
        )
        return (
            f"{candidate_name} {dimension_name} {query_focus} "
            f"AI application technology selection official docs production case 2026 {constraints}"
        ).strip()

    def _evaluate_candidate(
        self,
        *,
        context: DecisionContext,
        candidate_name: str,
        dimension_name: str,
        dimension_description: str,
        source_context: str,
        sources_summary: str,
    ) -> CandidateEvaluation:
        prompt = (
            "你是企业 AI 应用技术选型顾问。请基于用户约束和检索资料，"
            "评估一个候选技术在一个维度上的适配度。必须客观、克制，指出边界。\n\n"
            f"选型主题：{context.decision_topic}\n"
            f"项目类型：{context.project_type or '未提供'}\n"
            f"团队规模：{context.team_size or '未提供'}\n"
            f"时间要求：{context.timeline or '未提供'}\n"
            f"预算水平：{context.budget_level or '未提供'}\n"
            f"部署方式：{context.deployment_mode or '未提供'}\n"
            f"偏好语言：{context.preferred_language or '未提供'}\n"
            f"现有技术栈：{', '.join(context.existing_stack) or '未提供'}\n"
            f"特殊要求：{', '.join(context.requirements) or '未提供'}\n\n"
            f"候选技术：{candidate_name}\n"
            f"评估维度：{dimension_name}\n"
            f"维度说明：{dimension_description}\n\n"
            f"来源概览：\n{sources_summary or '暂无来源'}\n\n"
            f"检索上下文：\n{source_context or '暂无有效上下文'}\n\n"
            "请严格输出 JSON，不要输出 Markdown：\n"
            "{\n"
            '  "summary": "一句话说明该候选在此维度下的判断",\n'
            '  "pros": ["优势1", "优势2"],\n'
            '  "cons": ["不足1"],\n'
            '  "risks": ["风险1"],\n'
            '  "rating": "高|中高|中|中低|低",\n'
            '  "source_urls": ["https://..."]\n'
            "}"
        )

        try:
            response = self._invoke_text(prompt)
        except Exception:
            response = ""

        payload = self._parse_json_response(str(response))
        summary = str(payload.get("summary") or f"{candidate_name} 在{dimension_name}维度下适配度中等。")
        rating = str(payload.get("rating") or "中")
        if not RATING_PATTERN.fullmatch(rating):
            rating = "中"

        return CandidateEvaluation(
            candidate_name=candidate_name,
            dimension=dimension_name,
            summary=summary,
            pros=self._string_list(payload.get("pros")),
            cons=self._string_list(payload.get("cons")),
            risks=self._string_list(payload.get("risks")),
            rating=rating,
            source_urls=self._string_list(payload.get("source_urls")),
        )

    def _generate_report(self, state: DecisionState) -> str:
        matrix = state.comparison_matrix
        matrix_md = self._matrix_to_markdown(matrix)
        candidate_blocks = []
        for evaluation in state.evaluations:
            candidate_blocks.append(
                f"### {evaluation.candidate_name} - {evaluation.dimension}\n"
                f"- 评级：{evaluation.rating}\n"
                f"- 结论：{evaluation.summary}\n"
                f"- 优势：{'; '.join(evaluation.pros) or '暂无'}\n"
                f"- 不足：{'; '.join(evaluation.cons) or '暂无'}\n"
                f"- 风险：{'; '.join(evaluation.risks) or '暂无'}\n"
            )

        prompt = (
            "你是资深技术负责人，请生成一份面向 AI 应用技术栈选型的企业风格报告。"
            "报告必须包含：背景与约束、对比矩阵解读、推荐方案、备选方案、风险与待确认问题、来源引用。\n\n"
            f"选型上下文：\n{json.dumps(state.context.__dict__, ensure_ascii=False, indent=2)}\n\n"
            f"候选方案：{', '.join(candidate.name for candidate in state.candidates)}\n\n"
            f"对比矩阵：\n{matrix_md}\n\n"
            f"详细评估：\n{''.join(candidate_blocks)}\n\n"
            f"来源引用：\n{json.dumps(state.references, ensure_ascii=False, indent=2)}\n\n"
            "请输出 Markdown，结论要带适用边界，避免绝对化表达。"
        )

        try:
            report = self._invoke_text(prompt).strip()
        except Exception:
            report = ""

        if self.config.strip_thinking_tokens:
            report = strip_thinking_tokens(report)

        if report:
            return report

        recommended = self._pick_recommendation(state)
        return (
            f"# {state.context.decision_topic}\n\n"
            "## 背景与约束\n"
            f"- 项目类型：{state.context.project_type or '未提供'}\n"
            f"- 团队规模：{state.context.team_size or '未提供'}\n"
            f"- 时间要求：{state.context.timeline or '未提供'}\n"
            f"- 部署方式：{state.context.deployment_mode or '未提供'}\n\n"
            "## 候选方案对比矩阵\n"
            f"{matrix_md}\n\n"
            "## 推荐结论\n"
            f"建议优先考虑 **{recommended}**，但需要结合团队经验和实际验证结果做最终决策。\n\n"
            "## 风险与待确认问题\n"
            "- 需要验证候选技术在真实数据量和并发压力下的表现。\n"
            "- 需要确认团队是否具备对应技术栈的维护经验。\n"
            "- 需要进一步评估长期成本、许可证和供应商锁定风险。\n\n"
            "## 来源引用\n"
            + "\n".join(f"- [{ref.get('title')}]({ref.get('url')})" for ref in state.references[:20])
        )

    @staticmethod
    def _parse_json_response(text: str) -> dict[str, Any]:
        text = strip_thinking_tokens(text.strip())
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            return {}
        try:
            payload = json.loads(text[start : end + 1])
        except json.JSONDecodeError:
            return {}
        return payload if isinstance(payload, dict) else {}

    def _invoke_text(self, prompt: str) -> str:
        """Invoke HelloAgentsLLM with the message shape it expects."""

        return str(self.llm.invoke([{"role": "user", "content": prompt}]) or "")

    @staticmethod
    def _string_list(value: Any) -> list[str]:
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        if isinstance(value, str) and value.strip():
            return [value.strip()]
        return []

    @staticmethod
    def _extract_references(search_result: dict[str, Any] | None) -> list[dict[str, str]]:
        refs: list[dict[str, str]] = []
        for item in (search_result or {}).get("results", []):
            url = str(item.get("url") or "").strip()
            if not url:
                continue
            refs.append(
                {
                    "title": str(item.get("title") or url).strip(),
                    "url": url,
                    "domain": url.split("/")[2] if "://" in url else "",
                }
            )
        return refs

    @staticmethod
    def _matrix_to_markdown(matrix: dict[str, Any]) -> str:
        candidates = matrix.get("candidates") or []
        dimensions = matrix.get("dimensions") or []
        cells = matrix.get("cells") or {}
        header = "| 维度 | " + " | ".join(candidates) + " |"
        sep = "|---|" + "|".join("---" for _ in candidates) + "|"
        rows = [header, sep]
        for dimension in dimensions:
            row = [dimension]
            for candidate in candidates:
                row.append(str(cells.get(dimension, {}).get(candidate, "中")))
            rows.append("| " + " | ".join(row) + " |")
        return "\n".join(rows)

    @staticmethod
    def _pick_recommendation(state: DecisionState) -> str:
        score_map = {"高": 5, "中高": 4, "中": 3, "中低": 2, "低": 1}
        scores = {candidate.name: 0 for candidate in state.candidates}
        for evaluation in state.evaluations:
            scores[evaluation.candidate_name] = scores.get(evaluation.candidate_name, 0) + score_map.get(evaluation.rating, 3)
        if not scores:
            return "暂无推荐"
        return max(scores.items(), key=lambda item: item[1])[0]
