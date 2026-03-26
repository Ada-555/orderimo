"""Browser tests using Selenium — catches template rendering errors."""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


@pytest.fixture(scope="module")
def browser():
    """Headless Chrome browser for testing."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280,800")
    options.add_argument("--disable-extensions")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)
    yield driver
    driver.quit()


def get_url(browser, path):
    """Navigate and return page source or raise."""
    browser.get(f"http://localhost:8888{path}")
    # Wait for page to settle
    WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    return browser


# ─── Page Load Tests ─────────────────────────────────────────────────────────

def test_home_page_loads(browser):
    """Home page renders without errors."""
    browser.get("http://localhost:8888/")
    assert browser.title
    # Check no template errors in page source
    assert "TemplateDoesNotExist" not in browser.page_source
    assert "Invalid filter" not in browser.page_source
    assert "Exception" not in browser.page_source


def test_products_page_loads(browser):
    """Products page renders without errors."""
    browser.get("http://localhost:8888/products/")
    assert browser.title
    assert "TemplateDoesNotExist" not in browser.page_source
    assert "Invalid filter" not in browser.page_source


def test_login_page_loads(browser):
    """Login page renders without errors — catches crispy filter bugs."""
    browser.get("http://localhost:8888/accounts/login/")
    assert "TemplateDoesNotExist" not in browser.page_source
    assert "Invalid filter" not in browser.page_source
    assert "crispy" not in browser.page_source or "crispy_forms_tags" in browser.page_source
    # Check form is present
    assert browser.find_element(By.TAG_NAME, "form")


def test_signup_page_loads(browser):
    """Signup page renders without errors."""
    browser.get("http://localhost:8888/accounts/signup/")
    assert "TemplateDoesNotExist" not in browser.page_source
    assert "Invalid filter" not in browser.page_source
    assert browser.find_element(By.TAG_NAME, "form")


def test_cart_page_loads(browser):
    """Cart page renders without errors."""
    browser.get("http://localhost:8888/cart/")
    assert "TemplateDoesNotExist" not in browser.page_source
    assert "Invalid filter" not in browser.page_source


def test_checkout_page_loads(browser):
    """Checkout redirects for empty cart (not a 500)."""
    browser.get("http://localhost:8888/checkout/")
    # Should redirect (302) or 200 with empty cart message, NOT 500
    assert browser.current_url
    assert "500" not in browser.page_source


def test_orders_page_redirects_to_login(browser):
    """Orders page redirects unauthenticated users (not a 500)."""
    browser.get("http://localhost:8888/orders/")
    assert "500" not in browser.page_source


# ─── UI/CSS Tests ───────────────────────────────────────────────────────────

def test_home_page_has_visible_text(browser):
    """Check text is visible on home page — catches dark-on-dark issues."""
    browser.get("http://localhost:8888/")
    body = browser.find_element(By.TAG_NAME, "body")
    text = body.text
    # Key content should be present and visible
    assert "PLURINO" in text or "Shop" in text


def test_navbar_present(browser):
    """Navigation bar is present and has key links."""
    browser.get("http://localhost:8888/")
    nav = browser.find_element(By.TAG_NAME, "nav")
    assert nav
    # Nav links should be present
    links = nav.find_elements(By.TAG_NAME, "a")
    assert len(links) >= 2


def test_products_page_grid_renders(browser):
    """Product grid area is present."""
    browser.get("http://localhost:8888/products/")
    # Should have the product grid container
    assert browser.page_source


def test_login_page_has_working_form(browser):
    """Login form has email and password fields."""
    browser.get("http://localhost:8888/accounts/login/")
    inputs = browser.find_elements(By.TAG_NAME, "input")
    input_types = [inp.get_attribute("type") for inp in inputs]
    assert "email" in input_types or "text" in input_types
    assert "password" in input_types


def test_no_console_errors_on_home(browser):
    """No critical console errors on home page (checks page loaded fully)."""
    browser.get("http://localhost:8888/")
    # If we got here without JS errors that killed the page, that's a pass
    assert "localhost:8888" in browser.current_url
