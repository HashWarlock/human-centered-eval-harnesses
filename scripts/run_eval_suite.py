"""Run the deterministic eval behavior suite outside pytest."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from eval_harness.dataset import load_jsonl_cases
from eval_harness.judges import MockJudge, load_rubric
from eval_harness.metrics import exact_match, is_valid_json, normalized_exact_match, pass_fail_score
from eval_harness.runner import run_cases
from eval_harness.schemas import EvalCase, ScoreValue

ROOT = Path(__file__).resolve().parents[1]
DATASETS_DIR = ROOT / "tests" / "evals" / "datasets"
MOCKS_DIR = ROOT / "tests" / "evals" / "mocks"
RUBRICS_DIR = ROOT / "tests" / "evals" / "rubrics"
THRESHOLDS_PATH = ROOT / "configs" / "thresholds.yaml"
OUTPUT_PATH = ROOT / "outputs" / "eval_suite_summary.json"


def main() -> int:
    """Run the local deterministic eval suite and enforce configured thresholds."""
    thresholds = _load_thresholds()
    summary = _build_summary()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    failures = _check_thresholds(summary, thresholds)
    if failures:
        print("Deterministic eval suite failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Deterministic eval suite passed.")
    print(json.dumps(summary, indent=2))
    return 0


def _build_summary() -> dict[str, Any]:
    """Compute the behavior metrics used by the starter repo."""
    classification_observations = _evaluate_classification()
    generation_observations = _evaluate_generation()
    rag_metrics = _evaluate_rag()
    tool_metrics = _evaluate_tool()

    all_behavior = (
        classification_observations
        + generation_observations
        + rag_metrics["behavior"]
        + tool_metrics["behavior"]
    )
    return {
        "local_harness": {
            "behavior_rate": sum(all_behavior) / len(all_behavior),
        },
        "generation_eval": {
            "pass_rate": sum(generation_observations) / len(generation_observations),
        },
        "rag_eval": {
            "groundedness_rate": sum(rag_metrics["groundedness"])
            / len(rag_metrics["groundedness"]),
            "answer_correctness_rate": sum(rag_metrics["answer_correctness"])
            / len(rag_metrics["answer_correctness"]),
        },
        "tool_eval": {
            "tool_selection_rate": sum(tool_metrics["tool_selection"])
            / len(tool_metrics["tool_selection"]),
            "argument_correctness_rate": sum(tool_metrics["argument_correctness"])
            / len(tool_metrics["argument_correctness"]),
        },
    }


def _evaluate_classification() -> list[bool]:
    """Check whether classification behavior matches the labeled expectation."""
    cases = load_jsonl_cases(DATASETS_DIR / "classification_cases.jsonl")
    records = run_cases(cases, _predict, scorer=_classification_scorer)
    return [
        record.passed == case.metadata["expected_pass"]
        for case, record in zip(cases, records, strict=True)
    ]


def _evaluate_generation() -> list[bool]:
    """Check generation pass/fail behavior, including malformed JSON cases."""
    judge = _build_mock_judge()
    rubric = load_rubric(RUBRICS_DIR / "answer_quality.yaml")
    outputs = _load_mock_outputs()
    cases = load_jsonl_cases(DATASETS_DIR / "generation_cases.jsonl")

    observations: list[bool] = []
    for case in cases:
        actual = outputs[case.case_id]
        if case.metadata.get("requires_json"):
            observed_pass = is_valid_json(actual)
        else:
            observed_pass = judge.judge(case, actual, rubric).passed
        observations.append(observed_pass == case.metadata["expected_pass"])
    return observations


def _evaluate_rag() -> dict[str, list[bool]]:
    """Check groundedness and answer correctness for RAG cases."""
    judge = _build_mock_judge()
    rubric = load_rubric(RUBRICS_DIR / "answer_quality.yaml")
    outputs = _load_mock_outputs()
    cases = load_jsonl_cases(DATASETS_DIR / "rag_cases.jsonl")

    behavior: list[bool] = []
    groundedness: list[bool] = []
    answer_correctness: list[bool] = []
    for case in cases:
        result = judge.judge(case, outputs[case.case_id], rubric)
        behavior.append(result.passed == case.metadata["expected_pass"])
        groundedness.append(
            (result.scores["groundedness"] >= 0.5) == case.metadata["expected_groundedness"]
        )
        answer_correctness.append(
            (result.scores["answer_correctness"] >= 0.5)
            == case.metadata["expected_answer_correctness"]
        )
    return {
        "behavior": behavior,
        "groundedness": groundedness,
        "answer_correctness": answer_correctness,
    }


def _evaluate_tool() -> dict[str, list[bool]]:
    """Check tool selection and argument correctness behavior."""
    judge = _build_mock_judge()
    rubric = load_rubric(RUBRICS_DIR / "tool_correctness.yaml")
    outputs = _load_mock_outputs()
    cases = load_jsonl_cases(DATASETS_DIR / "tool_cases.jsonl")

    behavior: list[bool] = []
    tool_selection: list[bool] = []
    argument_correctness: list[bool] = []
    for case in cases:
        result = judge.judge(case, outputs[case.case_id], rubric)
        behavior.append(result.passed == case.metadata["expected_pass"])
        tool_selection.append(
            (result.scores["tool_selection"] >= 0.5) == case.metadata["expected_tool_selection"]
        )
        argument_correctness.append(
            (result.scores["argument_correctness"] >= 0.5)
            == case.metadata["expected_argument_correctness"]
        )
    return {
        "behavior": behavior,
        "tool_selection": tool_selection,
        "argument_correctness": argument_correctness,
    }


def _check_thresholds(summary: dict[str, Any], thresholds: dict[str, Any]) -> list[str]:
    """Return a list of threshold failures."""
    checks = [
        (
            "local_harness.behavior_rate",
            summary["local_harness"]["behavior_rate"],
            thresholds["local_harness"]["min_pass_rate"],
        ),
        (
            "generation_eval.pass_rate",
            summary["generation_eval"]["pass_rate"],
            thresholds["generation_eval"]["min_pass_rate"],
        ),
        (
            "rag_eval.groundedness_rate",
            summary["rag_eval"]["groundedness_rate"],
            thresholds["rag_eval"]["min_groundedness_rate"],
        ),
        (
            "rag_eval.answer_correctness_rate",
            summary["rag_eval"]["answer_correctness_rate"],
            thresholds["rag_eval"]["min_answer_correctness_rate"],
        ),
        (
            "tool_eval.tool_selection_rate",
            summary["tool_eval"]["tool_selection_rate"],
            thresholds["tool_eval"]["min_tool_selection_rate"],
        ),
        (
            "tool_eval.argument_correctness_rate",
            summary["tool_eval"]["argument_correctness_rate"],
            thresholds["tool_eval"]["min_argument_correctness_rate"],
        ),
    ]

    failures: list[str] = []
    for metric_name, observed, minimum in checks:
        if observed < minimum:
            failures.append(
                f"{metric_name}={observed:.3f} is below required threshold {minimum:.3f}"
            )
    return failures


def _load_thresholds() -> dict[str, Any]:
    """Load threshold configuration from YAML."""
    return yaml.safe_load(THRESHOLDS_PATH.read_text(encoding="utf-8"))


def _load_mock_outputs() -> dict[str, Any]:
    """Load deterministic model outputs from JSON fixtures."""
    return json.loads((MOCKS_DIR / "mock_model_outputs.json").read_text(encoding="utf-8"))


def _build_mock_judge() -> MockJudge:
    """Create a fixture-backed deterministic judge."""
    fixtures = json.loads((MOCKS_DIR / "mock_judge_outputs.json").read_text(encoding="utf-8"))
    return MockJudge(fixtures)


def _predict(case: EvalCase) -> Any:
    """Predict with fixture-backed outputs keyed by case id."""
    return _load_mock_outputs()[case.case_id]


def _classification_scorer(case: EvalCase, actual: Any) -> tuple[dict[str, ScoreValue], bool]:
    """Score classification outputs with exact and normalized exact match."""
    exact = pass_fail_score(exact_match(actual, case.expected))
    normalized = pass_fail_score(normalized_exact_match(actual, case.expected))
    passed = bool(normalized if case.metadata.get("match_type") == "normalized" else exact)
    return {"exact_match": exact, "normalized_exact_match": normalized}, passed


if __name__ == "__main__":
    raise SystemExit(main())
