# Contributing

This repository is meant to be extended. Keep changes deterministic by default and make behavior changes explicit in tests and fixtures.

## Add A Dataset

Create a new JSONL or CSV file under `tests/evals/datasets/`. Every case should include:

- a unique `case_id`
- a clear `task_type`
- a short `metadata.reason`
- explicit expectation fields in metadata when the suite is checking pass or fail behavior

If you add cases that depend on fixture-backed predictions, update `tests/evals/mocks/mock_model_outputs.json` as part of the same change.

## Add A Rubric

Create a YAML file under `tests/evals/rubrics/`. Keep the rubric small and local-first. If the rubric is meant for deterministic fixture mode, also add matching entries to `tests/evals/mocks/mock_judge_outputs.json`.

## Add A New Eval Case

Prefer adding the case first, then writing or updating the corresponding test. Include a reason in metadata so future contributors understand what regression or behavior the case is protecting.

## Update Golden Fixtures Safely

If a behavior change is intentional and the regression baselines must move:

```bash
python3 scripts/update_golden_files.py
git diff tests/regression/fixtures/
```

Review the JSON diff before committing. Do not update golden files casually just to make a failing regression test disappear.

## Change Thresholds Responsibly

Thresholds live in `configs/thresholds.yaml`. When changing them:

1. Explain why the old threshold is no longer appropriate
2. Show the observed metric values that motivated the change
3. Update docs or tests if the interpretation changed

Threshold changes should represent a deliberate policy decision, not a shortcut around a failing harness.

