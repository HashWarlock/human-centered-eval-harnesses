"""Aggregation helpers for deterministic eval results."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence
from typing import Any, TypeGuard

from eval_harness.schemas import ReportSummary, ResultRecord


def summarize_records(records: Sequence[ResultRecord]) -> ReportSummary:
    """Summarize result records into an aggregate report."""
    total_cases = len(records)
    passed_cases = sum(record.passed for record in records)
    failed_cases = total_cases - passed_cases
    pass_rate = passed_cases / total_cases if total_cases else 0.0

    return ReportSummary(
        total_cases=total_cases,
        passed_cases=passed_cases,
        failed_cases=failed_cases,
        pass_rate=pass_rate,
        average_scores=_average_numeric_scores(records),
        by_task_type=_group_by_task_type(records),
    )


def _average_numeric_scores(records: Sequence[ResultRecord]) -> dict[str, float]:
    """Average only numeric score values, ignoring bools and strings."""
    sums: defaultdict[str, float] = defaultdict(float)
    counts: defaultdict[str, int] = defaultdict(int)

    for record in records:
        for score_name, score_value in record.scores.items():
            if _is_numeric_score(score_value):
                sums[score_name] += float(score_value)
                counts[score_name] += 1

    return {
        score_name: sums[score_name] / counts[score_name]
        for score_name in sorted(sums)
        if counts[score_name] > 0
    }


def _group_by_task_type(records: Sequence[ResultRecord]) -> dict[str, Any]:
    """Build per-task summaries with the same core aggregate fields."""
    grouped: defaultdict[str, list[ResultRecord]] = defaultdict(list)
    for record in records:
        grouped[record.task_type].append(record)

    summary: dict[str, Any] = {}
    for task_type, task_records in sorted(grouped.items()):
        total_cases = len(task_records)
        passed_cases = sum(record.passed for record in task_records)
        failed_cases = total_cases - passed_cases
        summary[task_type] = {
            "total_cases": total_cases,
            "passed_cases": passed_cases,
            "failed_cases": failed_cases,
            "pass_rate": passed_cases / total_cases if total_cases else 0.0,
            "average_scores": _average_numeric_scores(task_records),
        }
    return summary


def _is_numeric_score(value: object) -> TypeGuard[int | float]:
    """Return ``True`` when the score is an int or float but not a bool."""
    return isinstance(value, (int, float)) and not isinstance(value, bool)
