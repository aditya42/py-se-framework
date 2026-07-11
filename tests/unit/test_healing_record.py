import json
from pathlib import Path
from types import SimpleNamespace

from selenium.webdriver.common.by import By

from ai_web_framework.ai.locator_healer import LocatorHealer


def test_healing_audit_record(tmp_path: Path):
    settings = SimpleNamespace(enabled=False, model="none", max_dom_chars=100, artifacts_dir=tmp_path)
    healer = LocatorHealer(driver=SimpleNamespace(), wait_seconds=1, settings=settings)
    healer._record((By.ID, "old"), (By.ID, "new"), "deterministic_fallback", 1.0)
    record = json.loads((tmp_path / "locator-healing.jsonl").read_text().strip())
    assert record["original_value"] == "old"
    assert record["recovered_value"] == "new"
