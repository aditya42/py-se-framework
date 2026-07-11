import pytest

from ai_web_framework.pages.shop_page import ShopPage


@pytest.mark.smoke
def test_valid_login(driver, settings, local_app_url):
    shop = ShopPage(driver, settings)
    shop.open(local_app_url)
    shop.login("demo", "secret")
    assert shop.login_message() == "Welcome, demo!"


@pytest.mark.regression
def test_product_search(driver, settings, local_app_url):
    shop = ShopPage(driver, settings)
    shop.open(local_app_url)
    shop.search("keyboard")
    assert shop.visible_product_names() == ["Mechanical Keyboard"]


@pytest.mark.regression
def test_add_product_to_cart(driver, settings, local_app_url):
    shop = ShopPage(driver, settings)
    shop.open(local_app_url)
    shop.add_product("USB-C Hub")
    assert shop.cart_count() == 1


@pytest.mark.ai
def test_deterministic_locator_healing(driver, settings, local_app_url):
    shop = ShopPage(driver, settings)
    shop.open(local_app_url)
    search = shop.find_search_with_healing()
    search.send_keys("stand")
    assert shop.visible_product_names() == ["Laptop Stand"]
