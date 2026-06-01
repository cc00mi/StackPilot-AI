"""Build comparison matrix structures for the frontend."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from models import CandidateEvaluation, CandidateOption, EvaluationDimension


def build_comparison_matrix(
    candidates: list[CandidateOption],
    dimensions: list[EvaluationDimension],
    evaluations: list[CandidateEvaluation],
) -> dict[str, Any]:
    """Convert candidate evaluations into a tabular matrix."""

    ratings: dict[str, dict[str, str]] = defaultdict(dict)
    summaries: dict[str, dict[str, str]] = defaultdict(dict)

    for evaluation in evaluations:
        ratings[evaluation.dimension][evaluation.candidate_name] = evaluation.rating
        summaries[evaluation.dimension][evaluation.candidate_name] = evaluation.summary

    return {
        "candidates": [candidate.name for candidate in candidates],
        "dimensions": [dimension.name for dimension in dimensions],
        "cells": {
            dimension.name: {
                candidate.name: ratings.get(dimension.name, {}).get(candidate.name, "中")
                for candidate in candidates
            }
            for dimension in dimensions
        },
        "summaries": {
            dimension.name: {
                candidate.name: summaries.get(dimension.name, {}).get(candidate.name, "")
                for candidate in candidates
            }
            for dimension in dimensions
        },
    }
