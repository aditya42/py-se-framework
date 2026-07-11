.PHONY: install test smoke regression ai lint format clean

install:
	python -m pip install --upgrade pip
	pip install -e ".[dev]"

install-browser:
	python scripts/check_browser.py

test:
	pytest -v --html=reports/report.html --self-contained-html

smoke:
	pytest -v -m smoke --html=reports/smoke-report.html --self-contained-html

regression:
	pytest -v -m regression --html=reports/regression-report.html --self-contained-html

ai:
	pytest -v -m ai --html=reports/ai-report.html --self-contained-html

unit:
	pytest -v tests/unit

lint:
	ruff check .
	mypy src

format:
	ruff format .
	ruff check --fix .

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache reports/*.html reports/screenshots/* reports/dom/* reports/ai/*
