from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from ai_web_framework.ai.openai_client import OpenAIJsonClient
from ai_web_framework.core.settings import AISettings


class FailureAnalyzer:
    def __init__(self, settings: AISettings) -> None:
        self.settings = settings
        self.settings.artifacts_dir.mkdir(parents=True, exist_ok=True)

    def analyze(self, test_name: str, error: str, current_url: str, dom: str) -> Path | None:
        if not self.settings.enabled:
            return None

        client = OpenAIJsonClient(self.settings.model)
        analysis = client.ask_json(
            instructions=(
                "Analyze Selenium test failures. Return JSON only with keys category, "
                "probable_cause, evidence, recommended_action, and confidence. Do not claim "
                "certainty when evidence is insufficient."
            ),
            prompt=(
                f"Test: {test_name}\nURL: {current_url}\nError: {error}\n"
                f"DOM snapshot:\n{dom[: self.settings.max_dom_chars]}"
            ),
        )
        output = {
            "test": test_name,
            "timestamp": datetime.now(UTC).isoformat(),
            "analysis": analysis,
        }
        safe_name = test_name.replace("/", "_").replace("::", "__")
        path = self.settings.artifacts_dir / f"failure-{safe_name}.json"
        path.write_text(json.dumps(output, indent=2), encoding="utf-8")
        return path
