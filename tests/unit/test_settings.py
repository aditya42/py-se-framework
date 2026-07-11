from ai_web_framework.core.settings import load_settings


def test_default_settings_are_ci_safe(monkeypatch):
    monkeypatch.delenv("AI_ENABLED", raising=False)
    settings = load_settings()
    assert settings.browser.headless is True
    assert settings.ai.enabled is False
    assert settings.ai.healing_mode == "suggest_only"
