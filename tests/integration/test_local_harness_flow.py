from __future__ import annotations

import json
from pathlib import Path

from eval_harness.aggregation import summarize_records
from eval_harness.dataset import load_jsonl_cases
from eval_harness.metrics import exact_match, normalized_exact_match, pass_fail_score
from eval_harness.reporting import write_csv_report, write_json_report, write_markdown_summary
from eval_harness.runner import run_cases


def test_full_local_harness_flow(tmp_path: Path) -> None:
    dataset_path = Path("tests/evals/datasets/classification_cases.jsonl")
    mock_outputs_path = Path("tests/evals/mocks/mock_model_outputs.json")
    mock_outputs = json.loads(mock_outputs_path.read_text(encoding="utf-8"))

    cases = load_jsonl_cases(dataset_path)

    def predict(case: object) -> object:
        return mock_outputs[case.case_id]  # type: ignore[attr-defined]

    def score(case: object, actual: object) -> tuple[dict[str, float], bool]:
        exact = pass_fail_score(exact_match(actual, case.expected))  # type: ignore[attr-defined]
        normalized = pass_fail_score(normalized_exact_match(actual, case.expected))  # type: ignore[attr-defined]
        passed = bool(normalized if case.metadata.get("match_type") == "normalized" else exact)  # type: ignore[attr-defined]
        return {"exact_match": exact, "normalized_exact_match": normalized}, passed

    records = run_cases(cases, predict, scorer=score)
    summary = summarize_records(records)

    json_path = tmp_path / "report.json"
    csv_path = tmp_path / "records.csv"
    markdown_path = tmp_path / "summary.md"

    write_json_report(json_path, records, summary)
    write_csv_report(csv_path, records)
    write_markdown_summary(markdown_path, summary)

    payload = json.loads(json_path.read_text(encoding="utf-8"))

    assert summary.total_cases == 3
    assert json_path.exists()
    assert csv_path.exists()
    assert markdown_path.exists()
    assert list(payload.keys()) == ["summary", "results"]
    assert payload["summary"]["total_cases"] == 3
    assert len(payload["results"]) == 3
