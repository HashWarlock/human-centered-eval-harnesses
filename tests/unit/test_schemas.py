from __future__ import annotations

import pytest
from pydantic import ValidationError

from eval_harness.schemas import EvalCase, ReportSummary, ResultRecord


def test_eval_case_defaults_are_stable() -> None:
    case = EvalCase(case_id="case-1", task_type="classification", input="hello", expected="world")

    assert case.tags == []
    assert case.metadata == {}


def test_eval_case_requires_string_case_id() -> None:
    with pytest.raises(ValidationError):
        EvalCase(case_id=123, task_type="classification", input="hello", expected="world")


def test_result_record_requires_metadata_field() -> None:
    with pytest.raises(ValidationError):
        ResultRecord(
            case_id="case-1",
            task_type="classification",
            actual="world",
            expected="world",
            scores={"exact_match": 1.0},
            passed=True,
            error=None,
        )


def test_report_summary_keeps_expected_shape() -> None:
    summary = ReportSummary(
        total_cases=2,
        passed_cases=1,
        failed_cases=1,
        pass_rate=0.5,
        average_scores={"exact_match": 0.5},
        by_task_type={"classification": {"pass_rate": 0.5}},
    )

    assert summary.model_dump() == {
        "total_cases": 2,
        "passed_cases": 1,
        "failed_cases": 1,
        "pass_rate": 0.5,
        "average_scores": {"exact_match": 0.5},
        "by_task_type": {"classification": {"pass_rate": 0.5}},
    }
