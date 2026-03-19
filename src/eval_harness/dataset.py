"""Dataset loading utilities for local deterministic eval cases."""

from __future__ import annotations

import csv
import json
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from eval_harness.exceptions import DatasetValidationError, DuplicateCaseIDError
from eval_harness.schemas import EvalCase


def validate_cases(
    raw_cases: Iterable[Mapping[str, Any]], source_name: str = "dataset"
) -> list[EvalCase]:
    """Validate raw records into ``EvalCase`` models."""
    validated: list[EvalCase] = []
    seen_case_ids: set[str] = set()

    for index, raw_case in enumerate(raw_cases, start=1):
        try:
            case = EvalCase(**dict(raw_case))
        except ValidationError as exc:
            raise DatasetValidationError(f"Invalid record {index} in {source_name}: {exc}") from exc
        if case.case_id in seen_case_ids:
            raise DuplicateCaseIDError(
                f"Duplicate case_id '{case.case_id}' found in {source_name} at record {index}"
            )
        seen_case_ids.add(case.case_id)
        validated.append(case)

    return validated


def load_jsonl_cases(path: str | Path) -> list[EvalCase]:
    """Load and validate cases from a JSONL file."""
    dataset_path = Path(path)
    raw_cases: list[Mapping[str, Any]] = []

    with dataset_path.open("r", encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError as exc:
                raise DatasetValidationError(
                    f"Invalid JSON on line {line_number} of {dataset_path}: {exc.msg}"
                ) from exc
            if not isinstance(payload, dict):
                raise DatasetValidationError(
                    f"Expected an object on line {line_number} of {dataset_path}"
                )
            raw_cases.append(payload)

    return validate_cases(raw_cases, source_name=str(dataset_path))


def load_csv_cases(path: str | Path) -> list[EvalCase]:
    """Load and validate cases from a CSV file with JSON-capable cells."""
    dataset_path = Path(path)
    raw_cases: list[dict[str, Any]] = []

    with dataset_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        required_columns = {"case_id", "task_type", "input", "expected"}
        if reader.fieldnames is None or not required_columns.issubset(set(reader.fieldnames)):
            raise DatasetValidationError(
                f"CSV dataset {dataset_path} must include columns: {sorted(required_columns)}"
            )

        for row in reader:
            raw_cases.append(
                {
                    "case_id": row.get("case_id"),
                    "task_type": row.get("task_type"),
                    "input": _coerce_csv_value(row.get("input")),
                    "expected": _coerce_csv_value(row.get("expected")),
                    "tags": _coerce_csv_list(row.get("tags")),
                    "metadata": _coerce_csv_mapping(row.get("metadata")),
                }
            )

    return validate_cases(raw_cases, source_name=str(dataset_path))


def _coerce_csv_value(raw_value: str | None) -> Any:
    """Parse JSON-shaped CSV cells while leaving plain strings intact."""
    if raw_value is None or raw_value == "":
        return None
    try:
        return json.loads(raw_value)
    except json.JSONDecodeError:
        return raw_value


def _coerce_csv_list(raw_value: str | None) -> list[str]:
    """Parse list-shaped CSV cells into string lists."""
    if raw_value is None or raw_value == "":
        return []
    value = _coerce_csv_value(raw_value)
    if not isinstance(value, list):
        raise DatasetValidationError("tags column must contain a JSON list")
    return [str(item) for item in value]


def _coerce_csv_mapping(raw_value: str | None) -> dict[str, Any]:
    """Parse mapping-shaped CSV cells into dictionaries."""
    if raw_value is None or raw_value == "":
        return {}
    value = _coerce_csv_value(raw_value)
    if not isinstance(value, dict):
        raise DatasetValidationError("metadata column must contain a JSON object")
    return value
