"""Stable Pydantic schemas used across the harness implementation and tests."""

from __future__ import annotations

from typing import Any, TypeAlias

from pydantic import BaseModel, ConfigDict, Field, model_validator

ScalarValue: TypeAlias = str | int | float | bool | None
StructuredValue: TypeAlias = dict[str, Any] | ScalarValue
ScoreValue: TypeAlias = float | bool | str | None


class EvalCase(BaseModel):
    """Represents a single evaluation example."""

    model_config = ConfigDict(extra="forbid")

    case_id: str
    task_type: str
    input: dict[str, Any] | str
    expected: StructuredValue
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_identifiers(self) -> EvalCase:
        """Reject empty identifiers that make debugging difficult."""
        if not self.case_id.strip():
            raise ValueError("case_id must not be empty")
        if not self.task_type.strip():
            raise ValueError("task_type must not be empty")
        return self


class ResultRecord(BaseModel):
    """Captures the outcome of running one case through the harness."""

    model_config = ConfigDict(extra="forbid")

    case_id: str
    task_type: str
    actual: StructuredValue
    expected: StructuredValue
    scores: dict[str, ScoreValue]
    passed: bool
    error: str | None
    metadata: dict[str, Any]


class ReportSummary(BaseModel):
    """Aggregated view of a batch of result records."""

    model_config = ConfigDict(extra="forbid")

    total_cases: int
    passed_cases: int
    failed_cases: int
    pass_rate: float
    average_scores: dict[str, float]
    by_task_type: dict[str, Any]

    @model_validator(mode="after")
    def validate_consistency(self) -> ReportSummary:
        """Keep aggregate counts internally consistent."""
        if self.total_cases < 0 or self.passed_cases < 0 or self.failed_cases < 0:
            raise ValueError("case counts must be non-negative")
        if self.passed_cases + self.failed_cases != self.total_cases:
            raise ValueError("passed_cases + failed_cases must equal total_cases")
        if not 0.0 <= self.pass_rate <= 1.0:
            raise ValueError("pass_rate must be between 0.0 and 1.0")
        return self
