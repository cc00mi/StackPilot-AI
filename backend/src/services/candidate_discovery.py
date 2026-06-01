"""Candidate discovery for AI technology selection decisions."""

from __future__ import annotations

from models import CandidateOption, DecisionContext


AI_TECH_CANDIDATE_PRESETS: dict[str, list[str]] = {
    "agent": ["LangChain", "LlamaIndex", "AutoGen", "CrewAI"],
    "rag": ["LlamaIndex", "LangChain", "Haystack", "Dify"],
    "向量": ["pgvector", "Milvus", "Weaviate", "Pinecone"],
    "vector": ["pgvector", "Milvus", "Weaviate", "Pinecone"],
    "模型": ["OpenAI API", "Ollama", "vLLM", "LM Studio"],
    "model": ["OpenAI API", "Ollama", "vLLM", "LM Studio"],
    "部署": ["Docker Compose", "Kubernetes", "Render", "VPS"],
    "deploy": ["Docker Compose", "Kubernetes", "Render", "VPS"],
    "后端": ["FastAPI", "Django", "NestJS", "Spring Boot"],
    "backend": ["FastAPI", "Django", "NestJS", "Spring Boot"],
}

DEFAULT_AI_CANDIDATES = ["LangChain", "LlamaIndex", "Dify", "AutoGen"]


def discover_candidates(context: DecisionContext) -> list[CandidateOption]:
    """Return explicit candidates or deterministic suggestions for the topic."""

    raw_candidates = [item.strip() for item in context.candidates if item.strip()]
    if not raw_candidates:
        topic = context.decision_topic.lower()
        for keyword, candidates in AI_TECH_CANDIDATE_PRESETS.items():
            if keyword.lower() in topic:
                raw_candidates = candidates
                break

    if not raw_candidates:
        raw_candidates = DEFAULT_AI_CANDIDATES

    unique: list[str] = []
    seen = set()
    for candidate in raw_candidates:
        normalized = candidate.strip()
        key = normalized.lower()
        if normalized and key not in seen:
            seen.add(key)
            unique.append(normalized)

    return [
        CandidateOption(
            name=name,
            category="AI 应用技术栈",
            description=f"{name} 作为本次选型候选方案之一。",
        )
        for name in unique[:5]
    ]
