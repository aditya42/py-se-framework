from __future__ import annotations

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.remote.webdriver import WebDriver

from ai_web_framework.core.settings import BrowserSettings


class DriverFactory:
    @staticmethod
    def create(settings: BrowserSettings) -> WebDriver:
        browser = settings.name.lower()

        if browser == "chrome":
            options = ChromeOptions()
            if settings.headless:
                options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument(f"--window-size={settings.window_width},{settings.window_height}")
            driver = webdriver.Chrome(options=options)
        elif browser == "firefox":
            options = FirefoxOptions()
            if settings.headless:
                options.add_argument("-headless")
            driver = webdriver.Firefox(options=options)
            driver.set_window_size(settings.window_width, settings.window_height)
        elif browser == "edge":
            options = EdgeOptions()
            if settings.headless:
                options.add_argument("--headless=new")
            options.add_argument(f"--window-size={settings.window_width},{settings.window_height}")
            driver = webdriver.Edge(options=options)
        else:
            raise ValueError(f"Unsupported browser: {settings.name}")

        driver.set_page_load_timeout(settings.page_load_timeout)
        return driver
