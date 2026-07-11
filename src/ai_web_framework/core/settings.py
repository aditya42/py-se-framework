from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[3]


def _as_bool(value: str | bool | None, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class BrowserSettings:
    name: str
    headless: bool
    window_width: int
    window_height: int
    explicit_wait: int
    page_load_timeout: int
    screenshot_on_failure: bool


@dataclass(frozen=True)
class AISettings:
    enabled: bool
    provider: str
    model: str
    healing_mode: str
    max_dom_chars: int
    artifacts_dir: Path


@dataclass(frozen=True)
class Settings:
    browser: BrowserSettings
    ai: AISettings
    base_url: str
    environment: str


def load_settings(config_path: str | Path | None = None) -> Settings:
    load_dotenv(ROOT_DIR / ".env")
    path = Path(config_path) if config_path else ROOT_DIR / "config" / "config.yaml"
    with path.open(encoding="utf-8") as stream:
        raw: dict[str, Any] = yaml.safe_load(stream) or {}

    browser = raw.get("browser", {})
    ai = raw.get("ai", {})
    execution = raw.get("execution", {})

    return Settings(
        browser=BrowserSettings(
            name=os.getenv("BROWSER", str(browser.get("name", "chrome"))).lower(),
            headless=_as_bool(os.getenv("HEADLESS"), bool(browser.get("headless", True))),
            window_width=int(browser.get("window_width", 1440)),
            window_height=int(browser.get("window_height", 1000)),
            explicit_wait=int(os.getenv("EXPLICIT_WAIT", browser.get("explicit_wait", 10))),
            page_load_timeout=int(
                os.getenv("PAGE_LOAD_TIMEOUT", browser.get("page_load_timeout", 30))
            ),
            screenshot_on_failure=_as_bool(browser.get("screenshot_on_failure"), True),
        ),
        ai=AISettings(
            enabled=_as_bool(os.getenv("AI_ENABLED"), bool(ai.get("enabled", False))),
            provider=os.getenv("AI_PROVIDER", str(ai.get("provider", "openai"))),
            model=os.getenv("AI_MODEL", str(ai.get("model", "gpt-5-mini"))),
            healing_mode=os.getenv(
                "AI_HEALING_MODE", str(ai.get("healing_mode", "suggest_only"))
            ),
            max_dom_chars=int(ai.get("max_dom_chars", 25000)),
            artifacts_dir=ROOT_DIR / str(ai.get("artifacts_dir", "reports/ai")),
        ),
        base_url=os.getenv("BASE_URL", str(execution.get("base_url", ""))),
        environment=str(execution.get("environment", "local")),
    )
