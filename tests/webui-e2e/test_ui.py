import pytest
from playwright.sync_api import sync_playwright


@pytest.fixture
def page():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        yield page
        browser.close()


def test_login_header_present(page):
    page.goto("http://localhost:8000/")

    login_header = page.query_selector("h2:text('Login')")
    assert login_header is not None
    assert login_header.is_visible()