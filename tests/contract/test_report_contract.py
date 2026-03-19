from __future__ import annotations

from eval_harness.schemas import ReportSummary


def test_report_summary_schema_contract() -> None:
    schema = ReportSummary.model_json_schema()

    assert list(schema["properties"].keys()) == [
        "total_cases",
        "passed_cases",
        "failed_cases",
        "pass_rate",
        "average_scores",
        "by_task_type",
    ]
    assert schema["required"] == [
        "total_cases",
        "passed_cases",
        "failed_cases",
        "pass_rate",
        "average_scores",
        "by_task_type",
    ]
