"""Regenerate deterministic regression fixtures from the local harness."""

from __future__ import annotations

import json
from pathlib import Path

from eval_harness.aggregation import summarize_records
from eval_harness.dataset import load_jsonl_cases
from eval_harness.metrics import (
    contains_match,
    exact_match,
    normalized_exact_match,
    pass_fail_score,
)
from eval_harness.schemas import EvalCase, ResultRecord

ROOT = Path(__file__).resolve().parents[1]
FIXTURES_DIR = ROOT / "tests" / "regression" / "fixtures"
MOCK_OUTPUTS_PATH = ROOT / "tests" / "evals" / "mocks" / "mock_model_outputs.json"
TARGET_CASE_IDS = ["cls_exact_pass", "cls_exact_fail", "gen_quality_pass"]


def main() -> int:
    """Rewrite the golden regression fixture files."""
    cases = _load_target_cases()
    mock_outputs = json.loads(MOCK_OUTPUTS_PATH.read_text(encoding="utf-8"))

    records: list[ResultRecord] = []
    for index, case in enumerate(cases, start=1):
        actual = mock_outputs[case.case_id]
        records.append(
            ResultRecord(
                case_id=case.case_id.replace("cls_", "golden-classification-").replace(
                    "gen_", "golden-generation-"
                ),
                task_type=case.task_type,
                actual=actual,
                expected=case.expected,
                scores={
                    "exact_match": pass_fail_score(exact_match(actual, case.expected)),
                    "normalized_exact_match": pass_fail_score(
                        normalized_exact_match(actual, case.expected)
                    ),
                    "contains_match": pass_fail_score(contains_match(actual, case.expected)),
                },
                passed=exact_match(actual, case.expected),
                error=None,
                metadata={"latency_ms": round(index / 10, 1), "raw_output": actual},
            )
        )

    summary = summarize_records(records)
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)
    (FIXTURES_DIR / "golden_results.json").write_text(
        json.dumps([record.model_dump() for record in records], indent=2), encoding="utf-8"
    )
    (FIXTURES_DIR / "expected_metrics.json").write_text(
        json.dumps(summary.model_dump(), indent=2), encoding="utf-8"
    )
    print("Updated regression fixtures.")
    return 0


def _load_target_cases() -> list[EvalCase]:
    """Load the canonical cases used for regression baselines."""
    classification_cases = load_jsonl_cases(
        ROOT / "tests" / "evals" / "datasets" / "classification_cases.jsonl"
    )
    generation_cases = load_jsonl_cases(
        ROOT / "tests" / "evals" / "datasets" / "generation_cases.jsonl"
    )
    all_cases = {case.case_id: case for case in classification_cases + generation_cases}
    return [all_cases[case_id] for case_id in TARGET_CASE_IDS]


if __name__ == "__main__":
    raise SystemExit(main())
