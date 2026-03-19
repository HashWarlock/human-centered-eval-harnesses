# Testing Strategy

This repository treats the harness and the eval suite as separate products. The tests are organized so both layers are validated independently.

## Unit Tests

Unit tests cover the lowest-level deterministic behavior:

- Pydantic schema validation
- JSONL and CSV dataset loading
- Metric correctness
- Aggregation rules

These tests should fail quickly and point to one small issue at a time.

## Integration Tests

Integration tests run a full local flow:

1. Load a dataset
2. Run a mock predictor
3. Score the results
4. Aggregate the batch
5. Write reports

This checks that the core components work together, not just in isolation.

## Contract Tests

Contract tests exist to catch accidental format drift. They fail when a stable schema or report shape changes unexpectedly. That is useful when notebooks, scripts, CI jobs, or downstream tools depend on a specific output format.

## Regression Tests

Regression tests compare current summaries against frozen golden fixtures. When behavior changes intentionally, contributors should update the golden files with the provided script and review the resulting diff carefully.

## Eval-Behavior Tests

The eval-behavior suite lives in `tests/evals/`. It uses canonical datasets, rubrics, and fixture-backed mock outputs to verify that the harness passes or fails the right examples across:

- classification
- generation
- RAG
- tool use

Negative and adversarial cases are first-class citizens. A good harness should fail the wrong answers consistently, not just pass the easy cases.

## Why Deterministic Local CI Comes First

Local deterministic CI is the best first gate because it is:

- fast
- cheap
- reproducible
- easy to debug

Live API evaluations are often worth adding later, but they should complement this baseline instead of replacing it.

