from __future__ import annotations

import json
from pathlib import Path

from eval_harness.reporting import write_csv_report, write_json_report
from eval_harness.schemas import ReportSummary, ResultRecord


def test_json_report_contract_is_stable(tmp_path: Path) -> None:
    records = [
        ResultRecord(
            case_id="case-1",
            task_type="classification",
            actual="positive",
            expected="positive",
            scores={"exact_match": 1.0},
            passed=True,
            error=None,
            metadata={"latency_ms": 0.1},
        )
    ]
    summary = ReportSummary(
        total_cases=1,
        passed_cases=1,
        failed_cases=0,
        pass_rate=1.0,
        average_scores={"exact_match": 1.0},
        by_task_type={"classification": {"pass_rate": 1.0}},
    )

    report_path = tmp_path / "report.json"
    write_json_report(report_path, records, summary)
    payload = json.loads(report_path.read_text(encoding="utf-8"))

    assert list(payload.keys()) == ["summary", "results"]
    assert list(payload["summary"].keys()) == [
        "total_cases",
        "passed_cases",
        "failed_cases",
        "pass_rate",
        "average_scores",
        "by_task_type",
    ]
    assert list(payload["results"][0].keys()) == [
        "case_id",
        "task_type",
        "actual",
        "expected",
        "scores",
        "passed",
        "error",
        "metadata",
    ]


def test_csv_report_contract_is_stable(tmp_path: Path) -> None:
    records = [
        ResultRecord(
            case_id="case-1",
            task_type="classification",
            actual="positive",
            expected="positive",
            scores={"exact_match": 1.0},
            passed=True,
            error=None,
            metadata={"latency_ms": 0.1},
        )
    ]

    report_path = tmp_path / "report.csv"
    write_csv_report(report_path, records)
    header = report_path.read_text(encoding="utf-8").splitlines()[0]

    assert header == "case_id,task_type,actual,expected,passed,error,scores,metadata"
