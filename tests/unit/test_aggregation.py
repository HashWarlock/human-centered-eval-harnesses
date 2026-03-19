from __future__ import annotations

from eval_harness.aggregation import summarize_records
from eval_harness.schemas import ResultRecord


def test_summarize_records_groups_by_task_type_and_averages_numeric_scores() -> None:
    records = [
        ResultRecord(
            case_id="case-1",
            task_type="classification",
            actual="positive",
            expected="positive",
            scores={"exact_match": 1.0, "judge_label": "pass", "judge_pass": True},
            passed=True,
            error=None,
            metadata={"latency_ms": 0.1},
        ),
        ResultRecord(
            case_id="case-2",
            task_type="classification",
            actual="negative",
            expected="positive",
            scores={"exact_match": 0.0, "judge_label": "fail", "judge_pass": False},
            passed=False,
            error=None,
            metadata={"latency_ms": 0.2},
        ),
        ResultRecord(
            case_id="case-3",
            task_type="generation",
            actual="answer",
            expected="answer",
            scores={"exact_match": 1.0},
            passed=True,
            error=None,
            metadata={"latency_ms": 0.3},
        ),
    ]

    summary = summarize_records(records)

    assert summary.total_cases == 3
    assert summary.passed_cases == 2
    assert summary.failed_cases == 1
    assert summary.pass_rate == 2 / 3
    assert summary.average_scores == {"exact_match": 2 / 3}
    assert summary.by_task_type["classification"]["pass_rate"] == 0.5
    assert summary.by_task_type["generation"]["passed_cases"] == 1


def test_summarize_records_handles_empty_inputs() -> None:
    summary = summarize_records([])

    assert summary.total_cases == 0
    assert summary.passed_cases == 0
    assert summary.failed_cases == 0
    assert summary.pass_rate == 0.0
    assert summary.average_scores == {}
    assert summary.by_task_type == {}
