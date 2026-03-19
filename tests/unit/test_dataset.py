from __future__ import annotations

from pathlib import Path

import pytest

from eval_harness.dataset import load_csv_cases, load_jsonl_cases, validate_cases
from eval_harness.exceptions import DatasetValidationError, DuplicateCaseIDError


def test_load_jsonl_cases_returns_validated_cases(tmp_path: Path) -> None:
    dataset_path = tmp_path / "cases.jsonl"
    dataset_path.write_text(
        "\n".join(
            [
                '{"case_id":"case-1","task_type":"classification","input":"hello","expected":"hello"}',
                '{"case_id":"case-2","task_type":"classification","input":{"text":"bye"},"expected":"bye"}',
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    cases = load_jsonl_cases(dataset_path)

    assert [case.case_id for case in cases] == ["case-1", "case-2"]
    assert cases[1].input == {"text": "bye"}


def test_load_jsonl_cases_rejects_duplicate_case_ids(tmp_path: Path) -> None:
    dataset_path = tmp_path / "duplicates.jsonl"
    dataset_path.write_text(
        "\n".join(
            [
                '{"case_id":"duplicate","task_type":"classification","input":"a","expected":"a"}',
                '{"case_id":"duplicate","task_type":"classification","input":"b","expected":"b"}',
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    with pytest.raises(DuplicateCaseIDError):
        load_jsonl_cases(dataset_path)


def test_load_csv_cases_parses_json_cells(tmp_path: Path) -> None:
    dataset_path = tmp_path / "cases.csv"
    dataset_path.write_text(
        (
            "case_id,task_type,input,expected,tags,metadata\n"
            'case-1,classification,"{""text"": ""hello""}","{""label"": ""positive""}",'
            '"[""smoke""]","{""source"": ""csv""}"\n'
        ),
        encoding="utf-8",
    )

    cases = load_csv_cases(dataset_path)

    assert cases[0].input == {"text": "hello"}
    assert cases[0].expected == {"label": "positive"}
    assert cases[0].tags == ["smoke"]
    assert cases[0].metadata == {"source": "csv"}


def test_validate_cases_raises_useful_error_for_invalid_record() -> None:
    with pytest.raises(DatasetValidationError, match="task_type"):
        validate_cases([{"case_id": "case-1", "input": "hello", "expected": "world"}])
