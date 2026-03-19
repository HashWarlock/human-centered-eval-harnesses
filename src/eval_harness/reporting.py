"""Writers for JSON, CSV, and Markdown eval reports."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from eval_harness.exceptions import ReportGenerationError
from eval_harness.schemas import ReportSummary, ResultRecord


def write_json_report(
    path: str | Path, records: list[ResultRecord], summary: ReportSummary
) -> Path:
    """Write a deterministic JSON report to disk."""
    output_path = Path(path)
    payload = {
        "summary": summary.model_dump(),
        "results": [record.model_dump() for record in records],
    }
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    except OSError as exc:
        raise ReportGenerationError(f"Could not write JSON report to {output_path}") from exc
    return output_path


def write_csv_report(path: str | Path, records: list[ResultRecord]) -> Path:
    """Write result records as a flat CSV file."""
    output_path = Path(path)
    headers = [
        "case_id",
        "task_type",
        "actual",
        "expected",
        "passed",
        "error",
        "scores",
        "metadata",
    ]

    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=headers)
            writer.writeheader()
            for record in records:
                writer.writerow(
                    {
                        "case_id": record.case_id,
                        "task_type": record.task_type,
                        "actual": _stringify(record.actual),
                        "expected": _stringify(record.expected),
                        "passed": record.passed,
                        "error": record.error or "",
                        "scores": json.dumps(record.scores, sort_keys=True),
                        "metadata": json.dumps(record.metadata, sort_keys=True),
                    }
                )
    except OSError as exc:
        raise ReportGenerationError(f"Could not write CSV report to {output_path}") from exc
    return output_path


def write_markdown_summary(path: str | Path, summary: ReportSummary) -> Path:
    """Write a short Markdown summary for humans."""
    output_path = Path(path)
    lines = [
        "# Eval Summary",
        "",
        f"- Total cases: {summary.total_cases}",
        f"- Passed cases: {summary.passed_cases}",
        f"- Failed cases: {summary.failed_cases}",
        f"- Pass rate: {summary.pass_rate:.2%}",
        "",
        "## Average Scores",
    ]

    if summary.average_scores:
        lines.extend(
            f"- {metric_name}: {metric_value:.3f}"
            for metric_name, metric_value in summary.average_scores.items()
        )
    else:
        lines.append("- No numeric scores were recorded.")

    lines.extend(["", "## By Task Type"])
    if summary.by_task_type:
        for task_type, task_summary in summary.by_task_type.items():
            lines.append(
                f"- {task_type}: "
                f"{task_summary['passed_cases']}/{task_summary['total_cases']} passed "
                f"({task_summary['pass_rate']:.2%})"
            )
    else:
        lines.append("- No task-specific breakdown was available.")

    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    except OSError as exc:
        raise ReportGenerationError(f"Could not write Markdown report to {output_path}") from exc
    return output_path


def _stringify(value: Any) -> str:
    """Serialize values into stable CSV cell strings."""
    if isinstance(value, str):
        return value
    return json.dumps(value, sort_keys=True)
