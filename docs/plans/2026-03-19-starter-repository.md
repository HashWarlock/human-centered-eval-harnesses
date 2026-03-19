# Human-Centered Eval Harnesses Starter Repository Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a complete deterministic starter repository for teaching modern AI evaluation harness design, including package code, tests, docs, notebooks, scripts, and CI.

**Architecture:** Use a `src/` Python package named `eval_harness` with Pydantic schemas at the center, deterministic local scoring logic, JSON/YAML fixtures for reproducible eval behavior, and lightweight scripts that orchestrate tests and notebook smoke runs. Keep the harness implementation and the eval suite separate in code organization and documentation so contributors can reason about the system boundary.

**Tech Stack:** Python 3.11+, pytest, pytest-cov, pydantic, ruff, mypy, nbformat, nbclient, jupyter, PyYAML

---

### Task 1: Project Scaffolding

**Files:**
- Create: `pyproject.toml`
- Create: `pytest.ini`
- Create: `Makefile`
- Create: `.gitignore`
- Create: `.pre-commit-config.yaml`
- Create: `.env.example`
- Create: `LICENSE`
- Create: `outputs/.gitkeep`

**Step 1: Write the scaffolding metadata and command surface**

Add Python packaging metadata, dev dependencies, pytest config, and Make targets required by the spec.

**Step 2: Run metadata-level checks**

Run: `python3 -m compileall src tests scripts`
Expected: package files compile once they exist

### Task 2: Tests and Fixtures First

**Files:**
- Create: `tests/unit/*.py`
- Create: `tests/integration/test_local_harness_flow.py`
- Create: `tests/contract/*.py`
- Create: `tests/regression/fixtures/*.json`
- Create: `tests/regression/test_regression_baselines.py`
- Create: `tests/evals/datasets/*.jsonl`
- Create: `tests/evals/rubrics/*.yaml`
- Create: `tests/evals/mocks/*.json`
- Create: `tests/evals/test_eval_harness_behavior.py`
- Create: `configs/thresholds.yaml`

**Step 1: Define the contract with failing tests**

Write tests that import `eval_harness` modules and assert stable schema, deterministic metrics, aggregation rules, end-to-end flow, regression baselines, and eval behavior expectations.

**Step 2: Verify the tests fail for the right reason**

Run: `pytest tests/unit/test_schemas.py -v`
Expected: FAIL because `eval_harness` package does not yet exist

### Task 3: Core Package Implementation

**Files:**
- Create: `src/eval_harness/__init__.py`
- Create: `src/eval_harness/schemas.py`
- Create: `src/eval_harness/exceptions.py`
- Create: `src/eval_harness/dataset.py`
- Create: `src/eval_harness/metrics.py`
- Create: `src/eval_harness/runner.py`
- Create: `src/eval_harness/judges.py`
- Create: `src/eval_harness/aggregation.py`
- Create: `src/eval_harness/reporting.py`

**Step 1: Implement the minimum code that satisfies schema and loader tests**

Build schemas and dataset validation first, then add metrics, runner, judge, aggregation, and reporting in small steps to satisfy the authored tests.

**Step 2: Re-run focused tests after each slice**

Run:
- `pytest tests/unit/test_schemas.py -v`
- `pytest tests/unit/test_dataset.py -v`
- `pytest tests/unit/test_metrics.py -v`
- `pytest tests/unit/test_aggregation.py -v`

Expected: each group turns green before moving on

### Task 4: Scripts, Docs, Notebooks, and CI

**Files:**
- Create: `scripts/run_eval_suite.py`
- Create: `scripts/check_notebooks.py`
- Create: `scripts/update_golden_files.py`
- Create: `README.md`
- Create: `docs/01-why-evaluation-matters.md`
- Create: `docs/02-what-is-an-eval-harness.md`
- Create: `docs/03-testing-strategy.md`
- Create: `docs/04-contributing.md`
- Create: `notebooks/*.ipynb`
- Create: `.github/workflows/*.yml`

**Step 1: Add teaching-oriented docs and executable notebooks**

Use the implemented package in notebooks and scripts so CI exercises the same local deterministic behavior users will learn from.

**Step 2: Add lightweight GitHub Actions**

Create fast workflows for quality checks, tests plus evals, and notebook smoke execution.

### Task 5: Full Verification

**Files:**
- Verify all created files

**Step 1: Install dependencies**

Run: `python3 -m pip install -e ".[dev]"`

**Step 2: Run repository verification**

Run:
- `make format`
- `make lint`
- `make typecheck`
- `make test`
- `make evals`
- `make notebooks`
- `make verify`

Expected: all commands exit successfully with deterministic results

**Step 3: Fix any issues and re-run**

No completion claim until fresh verification passes.
