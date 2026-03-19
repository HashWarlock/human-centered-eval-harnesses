from __future__ import annotations

from eval_harness.schemas import ResultRecord


def test_result_record_schema_contract() -> None:
    schema = ResultRecord.model_json_schema()

    assert list(schema["properties"].keys()) == [
        "case_id",
        "task_type",
        "actual",
        "expected",
        "scores",
        "passed",
        "error",
        "metadata",
    ]
    assert schema["required"] == [
        "case_id",
        "task_type",
        "actual",
        "expected",
        "scores",
        "passed",
        "error",
        "metadata",
    ]
