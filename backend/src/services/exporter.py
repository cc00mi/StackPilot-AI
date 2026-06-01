"""Export helpers for technology selection reports."""

from __future__ import annotations

import re
from pathlib import Path


def export_markdown_report(report: str, topic: str, output_dir: str = "./notes") -> str:
    """Persist a markdown report and return the file path."""

    if not report.strip():
        return ""

    safe_name = re.sub(r"[^\w\u4e00-\u9fff-]+", "_", topic).strip("_") or "tech_selection"
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    target = path / f"{safe_name}_selection_report.md"
    target.write_text(report, encoding="utf-8")
    return str(target)
