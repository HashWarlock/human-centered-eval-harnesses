# What Is An Eval Harness?

An evaluation harness is the repeatable machinery that takes a dataset of cases, runs a system under test, scores the outputs, aggregates the results, and writes reports that humans can review.

In this repository the harness has five core pieces:

## Dataset

The dataset defines the canonical cases you care about. Each `EvalCase` includes an identifier, task type, input, expected output, tags, and metadata. The metadata is important because it explains why the case exists and what behavior the suite expects.

## Runner

The runner is the execution boundary. It accepts an `EvalCase`, calls a local predictor, measures latency, captures raw output, and returns a stable `ResultRecord`. If the predictor raises an exception, the runner records a structured failure instead of hiding it.

## Metrics And Judge

Some tasks can be scored with deterministic metrics such as exact match, normalized exact match, substring checks, JSON validation, or numeric tolerance. Others need a rubric-like judgment layer. This project includes a deterministic `MockJudge` that loads frozen outputs from fixtures so the workflow is teachable and reproducible.

## Aggregation

After individual cases are scored, the harness aggregates them into a `ReportSummary`. That summary includes total cases, pass rate, average numeric scores, and grouped breakdowns by task type.

## Reporting

The final step is reporting. JSON is useful for downstream tooling, CSV is useful for spreadsheet-style review, and Markdown is useful for pull requests and human inspection.

## Review Loop

The review loop is simple:

1. Add or update dataset cases
2. Run the harness
3. Inspect records and summary reports
4. Tighten metrics, rubrics, or thresholds if needed
5. Repeat until the failures are informative instead of surprising

