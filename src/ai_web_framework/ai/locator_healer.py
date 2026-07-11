from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from ai_web_framework.ai.openai_client import OpenAIJsonClient
from ai_web_framework.core.settings import AISettings


@dataclass(frozen=True)
class HealingResult:
    original_by: str
    original_value: str
    recovered_by: str | None
    recovered_value: str | None
    strategy: str
    confidence: float
    timestamp: str


class LocatorHealer:
    """Recovers an element without modifying source code.

    Deterministic candidates are attempted first. Optional AI receives a bounded
    DOM snapshot and returns a single Selenium locator suggestion. Every attempt
    is written to reports/ai for review.
    """

    def __init__(self, driver: WebDriver, wait_seconds: int, settings: AISettings) -> None:
        self.driver = driver
        self.wait_seconds = wait_seconds
        self.settings = settings
        self.settings.artifacts_dir.mkdir(parents=True, exist_ok=True)

    def find(
        self,
        primary: tuple[str, str],
        *,
        semantic_name: str,
        fallbacks: list[tuple[str, str]] | None = None,
    ) -> WebElement:
        try:
            return WebDriverWait(self.driver, self.wait_seconds).until(
                EC.visibility_of_element_located(primary)
            )
        except (TimeoutException, NoSuchElementException):
            pass

        for candidate in fallbacks or []:
            try:
                element = WebDriverWait(self.driver, 2).until(
                    EC.visibility_of_element_located(candidate)
                )
                self._record(primary, candidate, "deterministic_fallback", 1.0)
                return element
            except (TimeoutException, NoSuchElementException):
                continue

        if self.settings.enabled:
            candidate, confidence = self._ask_ai(primary, semantic_name)
            if candidate:
                try:
                    element = WebDriverWait(self.driver, 3).until(
                        EC.visibility_of_element_located(candidate)
                    )
                    self._record(primary, candidate, "ai_suggestion", confidence)
                    return element
                except (TimeoutException, NoSuchElementException):
                    self._record(primary, None, "ai_suggestion_failed", confidence)

        self._record(primary, None, "unresolved", 0.0)
        raise NoSuchElementException(
            f"Could not locate '{semantic_name}' using primary, fallback, or enabled AI locators"
        )

    def _ask_ai(
        self, primary: tuple[str, str], semantic_name: str
    ) -> tuple[tuple[str, str] | None, float]:
        dom = self.driver.page_source[: self.settings.max_dom_chars]
        client = OpenAIJsonClient(self.settings.model)
        payload = client.ask_json(
            instructions=(
                "You are a conservative Selenium locator assistant. Return JSON only. "
                "Choose one stable locator based on id, name, data-testid, aria-label, role, "
                "or concise CSS. Never return JavaScript or XPath containing positional indexes."
            ),
            prompt=(
                f"Target semantic name: {semantic_name}\n"
                f"Failed locator: {primary}\n"
                "Return exactly: {\"by\": \"css selector|id|name|xpath\", "
                "\"value\": \"...\", \"confidence\": 0.0}\nDOM:\n"
                f"{dom}"
            ),
        )
        by = str(payload.get("by", "")).lower()
        value = str(payload.get("value", "")).strip()
        confidence = float(payload.get("confidence", 0.0))
        supported = {
            "css selector": By.CSS_SELECTOR,
            "id": By.ID,
            "name": By.NAME,
            "xpath": By.XPATH,
        }
        if by not in supported or not value or confidence < 0.7:
            return None, confidence
        return (supported[by], value), confidence

    def _record(
        self,
        original: tuple[str, str],
        recovered: tuple[str, str] | None,
        strategy: str,
        confidence: float,
    ) -> None:
        result = HealingResult(
            original_by=original[0],
            original_value=original[1],
            recovered_by=recovered[0] if recovered else None,
            recovered_value=recovered[1] if recovered else None,
            strategy=strategy,
            confidence=confidence,
            timestamp=datetime.now(UTC).isoformat(),
        )
        path = self.settings.artifacts_dir / "locator-healing.jsonl"
        with path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(asdict(result)) + "\n")
