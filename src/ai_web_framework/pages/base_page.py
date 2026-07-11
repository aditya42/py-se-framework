from __future__ import annotations

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from ai_web_framework.ai.locator_healer import LocatorHealer
from ai_web_framework.core.settings import Settings


class BasePage:
    def __init__(self, driver: WebDriver, settings: Settings) -> None:
        self.driver = driver
        self.settings = settings
        self.wait = WebDriverWait(driver, settings.browser.explicit_wait)
        self.healer = LocatorHealer(driver, settings.browser.explicit_wait, settings.ai)

    def open(self, url: str) -> None:
        self.driver.get(url)

    def visible(self, locator: tuple[str, str]) -> WebElement:
        return self.wait.until(EC.visibility_of_element_located(locator))

    def click(self, locator: tuple[str, str]) -> None:
        self.wait.until(EC.element_to_be_clickable(locator)).click()

    def type(self, locator: tuple[str, str], value: str) -> None:
        element = self.visible(locator)
        element.clear()
        element.send_keys(value)

    def text(self, locator: tuple[str, str]) -> str:
        return self.visible(locator).text.strip()
