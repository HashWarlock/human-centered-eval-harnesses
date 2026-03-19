"""Deterministic rubric loading and mock judge utilities."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field

from eval_harness.metrics import exact_match, normalized_exact_match
from eval_harness.schemas import EvalCase


class JudgeResult(BaseModel):
    """Structured output returned by the deterministic mock judge."""

    model_config = ConfigDict(extra="forbid")

    reasoning: str = ""
    scores: dict[str, float] = Field(default_factory=dict)
    passed: bool


def load_rubric(path: str | Path) -> dict[str, Any]:
    """Load a YAML rubric into a dictionary."""
    rubric_path = Path(path)
    payload = yaml.safe_load(rubric_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Rubric at {rubric_path} must deserialize to a mapping")
    return payload


def parse_structured_judge_output(output: str | Mapping[str, Any] | JudgeResult) -> JudgeResult:
    """Parse a structured judge payload from a dict, JSON string, or ``JudgeResult``."""
    if isinstance(output, JudgeResult):
        return output
    if isinstance(output, str):
        output = json.loads(output)
    if not isinstance(output, Mapping):
        raise ValueError("Judge output must be a mapping, JSON string, or JudgeResult")
    return JudgeResult(**dict(output))


class MockJudge:
    """Fixture-driven judge with deterministic fallback heuristics."""

    def __init__(self, fixture_outputs: Mapping[str, Any] | None = None) -> None:
        self.fixture_outputs = dict(fixture_outputs or {})

    def judge(self, case: EvalCase, actual: Any, rubric: Mapping[str, Any]) -> JudgeResult:
        """Return a predictable judgment for a case and model output."""
        if case.case_id in self.fixture_outputs:
            return parse_structured_judge_output(self.fixture_outputs[case.case_id])
        return self._heuristic_judge(case, actual, rubric)

    def _heuristic_judge(
        self, case: EvalCase, actual: Any, rubric: Mapping[str, Any]
    ) -> JudgeResult:
        """Fallback logic for examples that are not fixture-backed."""
        rubric_name = str(rubric.get("name", ""))
        if rubric_name == "tool_correctness":
            expected_tool = case.expected if isinstance(case.expected, dict) else {}
            actual_tool = actual if isinstance(actual, dict) else {}
            tool_selection = float(expected_tool.get("tool") == actual_tool.get("tool"))
            argument_correctness = float(expected_tool.get("args") == actual_tool.get("args"))
            passed = bool(tool_selection and argument_correctness)
            return JudgeResult(
                reasoning="Compared tool name and arguments using deterministic local logic.",
                scores={
                    "tool_selection": tool_selection,
                    "argument_correctness": argument_correctness,
                },
                passed=passed,
            )

        if case.task_type == "rag":
            expected_answer = (
                case.expected.get("answer") if isinstance(case.expected, dict) else case.expected
            )
            actual_answer = actual.get("answer") if isinstance(actual, dict) else actual
            evidence = actual.get("evidence", "") if isinstance(actual, dict) else ""
            contexts = case.input.get("context", []) if isinstance(case.input, dict) else []
            context_blob = " ".join(str(item) for item in contexts).lower()
            groundedness = float(
                str(actual_answer).lower() in context_blob and str(evidence).lower() in context_blob
            )
            answer_correctness = float(normalized_exact_match(actual_answer, expected_answer))
            passed = bool(groundedness and answer_correctness)
            return JudgeResult(
                reasoning=(
                    "Checked whether the answer and cited evidence appear in the provided context."
                ),
                scores={
                    "groundedness": groundedness,
                    "answer_correctness": answer_correctness,
                },
                passed=passed,
            )

        overall = float(exact_match(actual, case.expected))
        return JudgeResult(
            reasoning="Compared the model output directly against the labeled expectation.",
            scores={"rubric_score": overall},
            passed=bool(overall),
        )
