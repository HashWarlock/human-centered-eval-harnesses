"""Deterministic metric helpers for local evaluation."""

from __future__ import annotations

import json
import math
from typing import Any


def exact_match(actual: Any, expected: Any) -> bool:
    """Return ``True`` when two values are exactly equal."""
    return actual == expected


def normalized_exact_match(actual: Any, expected: Any) -> bool:
    """Compare values after deterministic whitespace and case normalization."""
    return _normalize_value(actual) == _normalize_value(expected)


def contains_match(actual: Any, expected_substring: Any) -> bool:
    """Return ``True`` when the expected substring is contained in the actual value."""
    return _normalize_value(expected_substring) in _normalize_value(actual)


def is_valid_json(candidate: Any) -> bool:
    """Return ``True`` when the candidate is valid JSON or JSON-serializable."""
    try:
        if isinstance(candidate, str):
            json.loads(candidate)
        else:
            json.dumps(candidate)
    except (TypeError, ValueError, json.JSONDecodeError):
        return False
    return True


def numeric_within_tolerance(actual: Any, expected: Any, tolerance: float = 0.0) -> bool:
    """Return ``True`` when two numeric values fall within the provided tolerance."""
    if not _is_number(actual) or not _is_number(expected):
        return False
    return math.isclose(float(actual), float(expected), abs_tol=tolerance)


def pass_fail(condition: bool) -> bool:
    """Return a stable boolean pass/fail view."""
    return bool(condition)


def pass_fail_score(condition: bool) -> float:
    """Return a numeric score view of a boolean result."""
    return 1.0 if condition else 0.0


def _normalize_value(value: Any) -> str:
    """Convert supported values into a deterministic comparable string."""
    if isinstance(value, str):
        return " ".join(value.strip().lower().split())
    if isinstance(value, dict):
        return json.dumps(value, sort_keys=True, separators=(",", ":")).lower()
    return str(value).strip().lower()


def _is_number(value: Any) -> bool:
    """Guard against treating booleans as numeric values."""
    return isinstance(value, (int, float)) and not isinstance(value, bool)
