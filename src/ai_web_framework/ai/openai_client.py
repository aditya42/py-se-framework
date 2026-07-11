from __future__ import annotations

import json
import os
from typing import Any

from openai import OpenAI


class OpenAIJsonClient:
    """Small adapter around the OpenAI Responses API.

    It is instantiated only when AI_ENABLED=true, keeping normal test execution
    independent from any external AI service.
    """

    def __init__(self, model: str) -> None:
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY is required when AI_ENABLED=true")
        self._client = OpenAI()
        self._model = model

    def ask_json(self, instructions: str, prompt: str) -> dict[str, Any]:
        response = self._client.responses.create(
            model=self._model,
            instructions=instructions,
            input=prompt,
        )
        text = response.output_text.strip()
        if text.startswith("```"):
            text = text.replace("```json", "", 1).replace("```", "").strip()
        return json.loads(text)
