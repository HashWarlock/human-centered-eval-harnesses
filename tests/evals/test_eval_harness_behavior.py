from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from eval_harness.dataset import load_jsonl_cases
from eval_harness.judges import MockJudge, load_rubric
from eval_harness.metrics import exact_match, is_valid_json, normalized_exact_match, pass_fail_score
from eval_harness.runner import run_cases

ROOT = Path(__file__).resolve().parents[2]
DATASETS_DIR = ROOT / "tests" / "evals" / "datasets"
MOCKS_DIR = ROOT / "tests" / "evals" / "mocks"
RUBRICS_DIR = ROOT / "tests" / "evals" / "rubrics"
THRESHOLDS_PATH = ROOT / "configs" / "thresholds.yaml"


def _load_thresholds() -> dict[str, Any]:
    return yaml.safe_load(THRESHOLDS_PATH.read_text(encoding="utf-8"))


def _load_mock_outputs() -> dict[str, Any]:
    return json.loads((MOCKS_DIR / "mock_model_outputs.json").read_text(encoding="utf-8"))


def _build_mock_judge() -> MockJudge:
    fixtures = json.loads((MOCKS_DIR / "mock_judge_outputs.json").read_text(encoding="utf-8"))
    return MockJudge(fixtures)


def _predictor(case: Any) -> Any:
    outputs = _load_mock_outputs()
    return outputs[case.case_id]


def _classification_scorer(case: Any, actual: Any) -> tuple[dict[str, float], bool]:
    exact = pass_fail_score(exact_match(actual, case.expected))
    normalized = pass_fail_score(normalized_exact_match(actual, case.expected))
    passed = bool(normalized if case.metadata.get("match_type") == "normalized" else exact)
    return {"exact_match": exact, "normalized_exact_match": normalized}, passed


def test_classification_cases_behave_as_expected() -> None:
    thresholds = _load_thresholds()
    cases = load_jsonl_cases(DATASETS_DIR / "classification_cases.jsonl")
    records = run_cases(cases, _predictor, scorer=_classification_scorer)

    behavior_rate = sum(
        record.passed == case.metadata["expected_pass"]
        for case, record in zip(cases, records, strict=True)
    ) / len(cases)

    assert behavior_rate >= thresholds["local_harness"]["min_pass_rate"]


def test_generation_cases_cover_correctness_and_structured_failures() -> None:
    thresholds = _load_thresholds()
    judge = _build_mock_judge()
    rubric = load_rubric(RUBRICS_DIR / "answer_quality.yaml")
    cases = load_jsonl_cases(DATASETS_DIR / "generation_cases.jsonl")
    outputs = _load_mock_outputs()

    observations: list[bool] = []
    for case in cases:
        actual = outputs[case.case_id]
        if case.metadata.get("requires_json"):
            observed_pass = is_valid_json(actual)
        else:
            observed_pass = judge.judge(case, actual, rubric).passed
        observations.append(observed_pass == case.metadata["expected_pass"])

    pass_rate = sum(observations) / len(observations)

    assert pass_rate >= thresholds["generation_eval"]["min_pass_rate"]


def test_rag_cases_measure_groundedness_and_answer_correctness() -> None:
    thresholds = _load_thresholds()
    judge = _build_mock_judge()
    rubric = load_rubric(RUBRICS_DIR / "answer_quality.yaml")
    cases = load_jsonl_cases(DATASETS_DIR / "rag_cases.jsonl")
    outputs = _load_mock_outputs()

    groundedness_hits: list[bool] = []
    correctness_hits: list[bool] = []
    for case in cases:
        result = judge.judge(case, outputs[case.case_id], rubric)
        grounded = result.scores["groundedness"] >= 0.5
        correct = result.scores["answer_correctness"] >= 0.5
        groundedness_hits.append(grounded == case.metadata["expected_groundedness"])
        correctness_hits.append(correct == case.metadata["expected_answer_correctness"])

    groundedness_rate = sum(groundedness_hits) / len(groundedness_hits)
    correctness_rate = sum(correctness_hits) / len(correctness_hits)

    assert groundedness_rate >= thresholds["rag_eval"]["min_groundedness_rate"]
    assert correctness_rate >= thresholds["rag_eval"]["min_answer_correctness_rate"]


def test_tool_cases_measure_tool_selection_and_argument_correctness() -> None:
    thresholds = _load_thresholds()
    judge = _build_mock_judge()
    rubric = load_rubric(RUBRICS_DIR / "tool_correctness.yaml")
    cases = load_jsonl_cases(DATASETS_DIR / "tool_cases.jsonl")
    outputs = _load_mock_outputs()

    tool_hits: list[bool] = []
    arg_hits: list[bool] = []
    for case in cases:
        result = judge.judge(case, outputs[case.case_id], rubric)
        tool_hits.append(
            (result.scores["tool_selection"] >= 0.5) == case.metadata["expected_tool_selection"]
        )
        arg_hits.append(
            (result.scores["argument_correctness"] >= 0.5)
            == case.metadata["expected_argument_correctness"]
        )

    tool_rate = sum(tool_hits) / len(tool_hits)
    arg_rate = sum(arg_hits) / len(arg_hits)

    assert tool_rate >= thresholds["tool_eval"]["min_tool_selection_rate"]
    assert arg_rate >= thresholds["tool_eval"]["min_argument_correctness_rate"]
