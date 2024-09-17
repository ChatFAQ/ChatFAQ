POETRY_RUN ?= poetry run

PYTHON_BIN ?= $(POETRY_RUN) python

format: isort black

black:
	$(PYTHON_BIN) -m black --exclude '/(\.git|\.hg|\.mypy_cache|\.nox|\.tox|\.venv|_build|buck-out|build|dist|node_modules|webpack_bundles)/' .

isort:
	$(PYTHON_BIN) -m isort chatfaq_sdk
	$(PYTHON_BIN) -m isort examples

run_example:
	$(PYTHON_BIN) examples/rag_example/__main__.py

run_holidays:
	$(PYTHON_BIN) examples/holidays/__main__.py
