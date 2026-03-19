PYTHON ?= python3

.PHONY: install format lint typecheck test evals notebooks verify

install:
	$(PYTHON) -m pip install -e ".[dev]"

format:
	$(PYTHON) -m ruff format src tests scripts

lint:
	PYTHONPATH=src $(PYTHON) -m ruff check src tests scripts

typecheck:
	PYTHONPATH=src $(PYTHON) -m mypy src scripts

test:
	PYTHONPATH=src $(PYTHON) -m pytest tests/unit tests/integration tests/contract tests/regression --cov=src/eval_harness --cov-report=term-missing

evals:
	PYTHONPATH=src $(PYTHON) -m pytest tests/evals -v
	PYTHONPATH=src $(PYTHON) scripts/run_eval_suite.py

notebooks:
	PYTHONPATH=src $(PYTHON) scripts/check_notebooks.py

verify:
	$(MAKE) lint
	$(MAKE) typecheck
	$(MAKE) test
	$(MAKE) evals
	$(MAKE) notebooks

