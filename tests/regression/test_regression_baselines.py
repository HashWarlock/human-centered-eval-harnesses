from __future__ import annotations

import json
from pathlib import Path

from eval_harness.aggregation import summarize_records
from eval_harness.schemas import ResultRecord


def test_regression_summary_matches_expected_metrics() -> None:
    golden_results_path = Path("tests/regression/fixtures/golden_results.json")
    expected_metrics_path = Path("tests/regression/fixtures/expected_metrics.json")

    golden_payload = json.loads(golden_results_path.read_text(encoding="utf-8"))
    expected_metrics = json.loads(expected_metrics_path.read_text(encoding="utf-8"))

    records = [ResultRecord(**item) for item in golden_payload]
    summary = summarize_records(records)

    assert summary.model_dump() == expected_metrics
