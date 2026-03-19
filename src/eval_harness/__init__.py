"""Deterministic starter package for local evaluation harnesses."""

from eval_harness.aggregation import summarize_records
from eval_harness.dataset import load_csv_cases, load_jsonl_cases, validate_cases
from eval_harness.exceptions import (
    DatasetValidationError,
    DuplicateCaseIDError,
    ReportGenerationError,
)
from eval_harness.judges import JudgeResult, MockJudge, load_rubric, parse_structured_judge_output
from eval_harness.metrics import (
    contains_match,
    exact_match,
    is_valid_json,
    normalized_exact_match,
    numeric_within_tolerance,
    pass_fail,
    pass_fail_score,
)
from eval_harness.reporting import write_csv_report, write_json_report, write_markdown_summary
from eval_harness.runner import run_case, run_cases
from eval_harness.schemas import EvalCase, ReportSummary, ResultRecord

__all__ = [
    "DatasetValidationError",
    "DuplicateCaseIDError",
    "EvalCase",
    "JudgeResult",
    "MockJudge",
    "ReportGenerationError",
    "ReportSummary",
    "ResultRecord",
    "contains_match",
    "exact_match",
    "is_valid_json",
    "load_csv_cases",
    "load_jsonl_cases",
    "load_rubric",
    "normalized_exact_match",
    "numeric_within_tolerance",
    "parse_structured_judge_output",
    "pass_fail",
    "pass_fail_score",
    "run_case",
    "run_cases",
    "summarize_records",
    "validate_cases",
    "write_csv_report",
    "write_json_report",
    "write_markdown_summary",
]
