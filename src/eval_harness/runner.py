"""Local callable runner for deterministic eval cases."""

from __future__ import annotations

import time
from collections.abc import Callable, Sequence
from typing import Any

from eval_harness.metrics import exact_match, pass_fail_score
from eval_harness.schemas import EvalCase, ResultRecord, ScoreValue

Scorer = Callable[[EvalCase, Any], tuple[dict[str, ScoreValue], bool]]
Predictor = Callable[[EvalCase], Any]


def run_case(case: EvalCase, predictor: Predictor, scorer: Scorer | None = None) -> ResultRecord:
    """Run one case through the predictor and optional scorer."""
    active_scorer = scorer or _default_scorer
    start_time = time.perf_counter()

    try:
        actual = predictor(case)
        scores, passed = active_scorer(case, actual)
        error = None
        raw_output = actual
    except Exception as exc:  # noqa: BLE001
        actual = None
        scores = {"execution_succeeded": 0.0}
        passed = False
        error = f"{exc.__class__.__name__}: {exc}"
        raw_output = None

    latency_ms = round((time.perf_counter() - start_time) * 1000, 3)

    return ResultRecord(
        case_id=case.case_id,
        task_type=case.task_type,
        actual=actual,
        expected=case.expected,
        scores=scores,
        passed=passed,
        error=error,
        metadata={"latency_ms": latency_ms, "raw_output": raw_output},
    )


def run_cases(
    cases: Sequence[EvalCase], predictor: Predictor, scorer: Scorer | None = None
) -> list[ResultRecord]:
    """Run a batch of cases through the local predictor."""
    return [run_case(case, predictor, scorer=scorer) for case in cases]


def _default_scorer(case: EvalCase, actual: Any) -> tuple[dict[str, ScoreValue], bool]:
    """Fallback exact-match scorer used when no scorer is supplied."""
    matched = exact_match(actual, case.expected)
    score = pass_fail_score(matched)
    return {"exact_match": score}, matched
