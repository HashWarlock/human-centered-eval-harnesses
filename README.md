# human-centered-eval-harnesses

`human-centered-eval-harnesses` is a guided learning repository for understanding how modern AI evaluation harnesses are assembled, tested, and extended without depending on live model APIs. It ships with a minimal Python reference implementation, a deterministic eval suite, starter notebooks, and CI that gates pushes and pull requests.

This repository deliberately contains two products:

1. The harness implementation in `src/eval_harness/`
2. The eval suite in `tests/evals/` that judges whether the harness behaves as expected

That split matters. A harness can be syntactically valid and still fail the behavior suite. The project is designed to teach that distinction early.

## Quickstart

```bash
python3 -m pip install -e ".[dev]"
make format
make verify
```

## Commands

```bash
make install      # install package and development dependencies
make format       # apply ruff formatting
make lint         # run ruff checks
make typecheck    # run mypy on src/ and scripts/
make test         # run unit, integration, contract, and regression tests
make evals        # run deterministic eval-behavior tests and CLI suite
make notebooks    # execute starter notebooks with nbclient
make verify       # lint + typecheck + tests + evals + notebooks
python3 scripts/update_golden_files.py
```

## Testing Philosophy

The repository prefers deterministic local mocks and frozen fixtures before any live integration. That keeps CI fast, reproducible, and educational. Contributors can add live or stochastic paths later, but the baseline should stay local-first:

- Unit tests lock down schema, dataset, metric, and aggregation behavior.
- Integration tests exercise a full local harness flow from dataset to report.
- Contract tests fail when stable output formats drift unintentionally.
- Regression tests compare summary outputs against frozen golden fixtures.
- Eval-behavior tests treat the harness and the eval suite as separate products.

## Repo Layout

```text
src/eval_harness/         Reference implementation
tests/evals/              Deterministic behavior suite, rubrics, mocks, datasets
tests/regression/         Frozen fixture baselines
notebooks/                Executable teaching notebooks
scripts/                  Local automation helpers
docs/                     Project guides and contributor docs
.github/workflows/        Push and pull request gates
```

## Extending The Project

Start by adding or editing a deterministic dataset case, rubric, or mock output. Then update or add tests before changing the harness implementation. If the intended behavior truly changes, regenerate the golden fixtures with `python3 scripts/update_golden_files.py` and review the diff carefully.

