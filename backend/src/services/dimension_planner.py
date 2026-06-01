"""Evaluation dimension planning for technology selection."""

from __future__ import annotations

from models import DecisionContext, EvaluationDimension


DEFAULT_DIMENSIONS = [
    (
        "开发效率",
        "评估候选技术能否帮助团队快速交付 AI 应用 MVP。",
        "developer productivity quick implementation AI application",
    ),
    (
        "AI 集成友好度",
        "评估候选技术对 LLM、RAG、Agent、工具调用和工作流编排的支持。",
        "LLM RAG agent tool calling integration support",
    ),
    (
        "生态与成熟度",
        "评估社区活跃度、官方文档、案例、插件和长期维护风险。",
        "ecosystem maturity documentation community production adoption",
    ),
    (
        "部署与运维复杂度",
        "评估部署方式、监控、扩缩容、私有化和团队维护成本。",
        "deployment operations scalability observability self hosting",
    ),
    (
        "成本与风险",
        "评估学习成本、迁移成本、供应商锁定、许可证和关键风险。",
        "cost risks lock-in license learning curve",
    ),
]


def plan_dimensions(context: DecisionContext) -> list[EvaluationDimension]:
    """Build the MVP dimension set, lightly tailored by context."""

    dimensions = [
        EvaluationDimension(
            id=index,
            name=name,
            description=description,
            query_focus=query_focus,
        )
        for index, (name, description, query_focus) in enumerate(DEFAULT_DIMENSIONS, start=1)
    ]

    if context.deployment_mode:
        dimensions[3].description += f" 本次部署约束：{context.deployment_mode}。"
    if context.budget_level:
        dimensions[4].description += f" 本次预算约束：{context.budget_level}。"

    return dimensions
