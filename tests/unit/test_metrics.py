from __future__ import annotations

from eval_harness.metrics import (
    contains_match,
    exact_match,
    is_valid_json,
    normalized_exact_match,
    numeric_within_tolerance,
    pass_fail,
    pass_fail_score,
)


def test_exact_match_is_deterministic() -> None:
    assert exact_match("hello", "hello") is True
    assert exact_match("hello", "world") is False


def test_normalized_exact_match_ignores_case_and_whitespace() -> None:
    assert normalized_exact_match("  Blue ", "blue") is True
    assert normalized_exact_match("blue", "green") is False


def test_contains_match_works_for_substrings() -> None:
    assert contains_match("The harness is deterministic.", "deterministic") is True
    assert contains_match("The harness is deterministic.", "random") is False


def test_is_valid_json_detects_malformed_payloads() -> None:
    assert is_valid_json('{"answer": "ok"}') is True
    assert is_valid_json('{"answer": "ok"') is False


def test_numeric_within_tolerance_respects_bounds() -> None:
    assert numeric_within_tolerance(10.0, 10.1, tolerance=0.2) is True
    assert numeric_within_tolerance(10.0, 10.4, tolerance=0.2) is False


def test_pass_fail_helpers_return_bool_and_float_views() -> None:
    assert pass_fail(True) is True
    assert pass_fail(False) is False
    assert pass_fail_score(True) == 1.0
    assert pass_fail_score(False) == 0.0
