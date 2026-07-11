# Selenium AI Web Framework — Python

Web UI automation framework using **Python, Selenium, pytest, Page Objects, HTML reports, screenshots, CI, and optional AI-assisted diagnostics**.

## What is included

- Selenium WebDriver with Chrome, Firefox, and Edge support
- pytest fixtures, markers, parallel execution support, and HTML reports
- Page Object Model with explicit waits
- Deterministic local sample web application; no external test site required
- Failure screenshots and DOM snapshots
- Auditable locator recovery with deterministic fallback first
- Optional OpenAI-based locator suggestions and failure classification
- GitHub Actions pull-request workflow
- Ruff, mypy, pre-commit, `.env.example`, Makefile, and MIT license

## Design rule for AI

AI is **off by default**. Normal tests do not require a model or API key. Locator recovery never edits source files or silently replaces selectors. Every recovery is written to `reports/ai/locator-healing.jsonl` for human review.

## Project structure

```text
selenium-ai-web-framework/
├── .github/workflows/tests.yml
├── config/config.yaml
├── src/ai_web_framework/
│   ├── ai/
│   │   ├── failure_analyzer.py
│   │   ├── locator_healer.py
│   │   └── openai_client.py
│   ├── core/
│   │   ├── driver_factory.py
│   │   └── settings.py
│   └── pages/
│       ├── base_page.py
│       └── shop_page.py
├── tests/
│   ├── e2e/test_shop.py
│   ├── unit/
│   ├── resources/sample_shop.html
│   └── conftest.py
├── .env.example
├── Makefile
├── pyproject.toml
└── README.md
```

## Local setup

```bash
python3 -m venv .venv
source .venv/bin/activate        # macOS/Linux
# .venv\Scripts\activate         # Windows PowerShell

python -m pip install --upgrade pip
pip install -e ".[dev]"
cp .env.example .env
```

Install Chrome, Firefox, or Edge. Selenium Manager resolves the matching driver automatically when tests start.

## Run tests

```bash
make unit
make smoke
make regression
make ai
make test
```

Direct pytest examples:

```bash
pytest -v -m smoke
pytest -v tests/e2e/test_shop.py::test_product_search
pytest -v -n auto --html=reports/report.html --self-contained-html
```

The sample tests start a local HTTP server automatically and exercise:

1. Valid login
2. Product filtering
3. Add-to-cart behavior
4. Recovery from an obsolete locator using an approved deterministic fallback

## Enable optional AI diagnostics

Create `.env` from `.env.example` and set:

```dotenv
AI_ENABLED=true
OPENAI_API_KEY=your_key_here
AI_MODEL=gpt-5-mini
AI_HEALING_MODE=suggest_only
```

Then run:

```bash
pytest -v -m ai
```

The implementation uses the OpenAI Python SDK's Responses API. Keep the API key in environment variables or a CI secret—never in source control.

## Using a real application

Set `BASE_URL` in `.env`:

```dotenv
BASE_URL=https://qa.example.com
```

When `BASE_URL` is empty, the bundled deterministic sample application is used. For a real project, add page objects under `src/ai_web_framework/pages/` and domain tests under `tests/e2e/`.

## CI

`.github/workflows/tests.yml` runs on pull requests and pushes to `main`. It performs linting, unit tests, headless Chrome smoke tests, and uploads reports as build artifacts.

Add `OPENAI_API_KEY` as a GitHub Actions secret only if a separate opt-in AI job is introduced. The default CI deliberately runs with `AI_ENABLED=false`.

## Recommended production controls

- Use `data-testid`, accessible names, or stable IDs as primary locators.
- Treat AI output as a suggestion, not an assertion of correctness.
- Never auto-commit healed locators.
- Cap DOM data sent to an external model and remove sensitive content.
- Keep smoke tests independent of AI and external services.
- Review `reports/ai/locator-healing.jsonl` before changing page objects.
