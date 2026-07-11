from __future__ import annotations

from selenium.webdriver.common.by import By

from ai_web_framework.pages.base_page import BasePage


class ShopPage(BasePage):
    USERNAME = (By.ID, "username")
    PASSWORD = (By.ID, "password")
    LOGIN = (By.CSS_SELECTOR, "button[data-testid='login-button']")
    LOGIN_MESSAGE = (By.ID, "login-message")
    SEARCH = (By.CSS_SELECTOR, "input[data-testid='product-search']")
    PRODUCT_CARDS = (By.CSS_SELECTOR, "[data-testid='product-card']")
    CART_COUNT = (By.ID, "cart-count")

    def login(self, username: str, password: str) -> None:
        self.type(self.USERNAME, username)
        self.type(self.PASSWORD, password)
        self.click(self.LOGIN)

    def login_message(self) -> str:
        return self.text(self.LOGIN_MESSAGE)

    def search(self, term: str) -> None:
        self.type(self.SEARCH, term)

    def visible_product_names(self) -> list[str]:
        return [element.get_attribute("data-name") or "" for element in self.driver.find_elements(*self.PRODUCT_CARDS) if element.is_displayed()]

    def add_product(self, product_name: str) -> None:
        locator = (
            By.CSS_SELECTOR,
            f"button[data-product='{product_name}'][data-testid='add-to-cart']",
        )
        self.click(locator)

    def cart_count(self) -> int:
        return int(self.text(self.CART_COUNT))

    def find_search_with_healing(self):
        obsolete = (By.ID, "old-product-search")
        fallbacks = [self.SEARCH, (By.NAME, "productSearch")]
        return self.healer.find(obsolete, semantic_name="product search input", fallbacks=fallbacks)
