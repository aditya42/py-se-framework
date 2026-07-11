from __future__ import annotations

import os
import socket
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Generator

import pytest
from selenium.webdriver.remote.webdriver import WebDriver

from ai_web_framework.ai.failure_analyzer import FailureAnalyzer
from ai_web_framework.core.driver_factory import DriverFactory
from ai_web_framework.core.settings import Settings, load_settings

ROOT = Path(__file__).resolve().parents[1]


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        return


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


@pytest.fixture(scope="session")
def settings() -> Settings:
    return load_settings()


@pytest.fixture(scope="session")
def local_app_url(settings: Settings) -> Generator[str, None, None]:
    if settings.base_url:
        yield settings.base_url
        return

    port = _free_port()
    app_dir = ROOT / "tests" / "resources"
    previous = Path.cwd()
    os.chdir(app_dir)
    server = ThreadingHTTPServer(("127.0.0.1", port), QuietHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{port}/sample_shop.html"
    finally:
        server.shutdown()
        thread.join(timeout=5)
        os.chdir(previous)


@pytest.fixture
def driver(settings: Settings, request: pytest.FixtureRequest) -> Generator[WebDriver, None, None]:
    browser = DriverFactory.create(settings.browser)
    yield browser

    if getattr(request.node, "rep_call", None) and request.node.rep_call.failed:
        reports = ROOT / "reports"
        (reports / "screenshots").mkdir(parents=True, exist_ok=True)
        (reports / "dom").mkdir(parents=True, exist_ok=True)
        safe_name = request.node.nodeid.replace("/", "_").replace("::", "__")
        browser.save_screenshot(str(reports / "screenshots" / f"{safe_name}.png"))
        (reports / "dom" / f"{safe_name}.html").write_text(
            browser.page_source, encoding="utf-8"
        )
        FailureAnalyzer(settings.ai).analyze(
            request.node.nodeid,
            str(request.node.rep_call.longrepr),
            browser.current_url,
            browser.page_source,
        )
    browser.quit()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)
