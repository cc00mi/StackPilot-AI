"""State models used by the deep research workflow."""

import operator
from dataclasses import dataclass, field
from typing import Any, List, Optional

from typing_extensions import Annotated


@dataclass(kw_only=True)
class TodoItem:
    """单个待办任务项。"""

    id: int
    title: str
    intent: str
    query: str
    status: str = field(default="pending")
    summary: Optional[str] = field(default=None)
    sources_summary: Optional[str] = field(default=None)
    notices: list[str] = field(default_factory=list)
    note_id: Optional[str] = field(default=None)
    note_path: Optional[str] = field(default=None)
    stream_token: Optional[str] = field(default=None)


@dataclass(kw_only=True)
class SummaryState:
    research_topic: str = field(default=None)  # Report topic
    search_query: str = field(default=None)  # Deprecated placeholder
    web_research_results: Annotated[list, operator.add] = field(default_factory=list)
    sources_gathered: Annotated[list, operator.add] = field(default_factory=list)
    research_loop_count: int = field(default=0)  # Research loop count
    running_summary: str = field(default=None)  # Legacy summary field
    todo_items: Annotated[list, operator.add] = field(default_factory=list)
    structured_report: Optional[str] = field(default=None)
    report_note_id: Optional[str] = field(default=None)
    report_note_path: Optional[str] = field(default=None)


@dataclass(kw_only=True)
class SummaryStateInput:
    research_topic: str = field(default=None)  # Report topic


@dataclass(kw_only=True)
class SummaryStateOutput:
    running_summary: str = field(default=None)  # Backward-compatible文本
    report_markdown: Optional[str] = field(default=None)
    todo_items: List[TodoItem] = field(default_factory=list)


@dataclass(kw_only=True)
class DecisionContext:
    """Structured context for an AI technology selection decision."""

    decision_topic: str
    project_type: str = ""
    team_size: str = ""
    timeline: str = ""
    budget_level: str = ""
    deployment_mode: str = ""
    preferred_language: str = ""
    existing_stack: list[str] = field(default_factory=list)
    requirements: list[str] = field(default_factory=list)
    candidates: list[str] = field(default_factory=list)


@dataclass(kw_only=True)
class CandidateOption:
    """A candidate technology to evaluate."""

    name: str
    category: str = "AI 应用技术"
    description: str = ""


@dataclass(kw_only=True)
class EvaluationDimension:
    """A decision dimension used to compare candidates."""

    id: int
    name: str
    description: str
    query_focus: str


@dataclass(kw_only=True)
class CandidateEvaluation:
    """Evaluation result for one candidate under one dimension."""

    candidate_name: str
    dimension: str
    summary: str
    pros: list[str] = field(default_factory=list)
    cons: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    rating: str = "中"
    source_urls: list[str] = field(default_factory=list)


@dataclass(kw_only=True)
class DecisionState:
    """Runtime state for the technology selection workflow."""

    context: DecisionContext
    candidates: list[CandidateOption] = field(default_factory=list)
    dimensions: list[EvaluationDimension] = field(default_factory=list)
    evaluations: list[CandidateEvaluation] = field(default_factory=list)
    comparison_matrix: dict[str, Any] = field(default_factory=dict)
    report_markdown: str = ""
    references: list[dict[str, str]] = field(default_factory=list)

