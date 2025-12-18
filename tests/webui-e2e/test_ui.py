import pytest
from playwright.sync_api import sync_playwright


@pytest.fixture
def page():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        yield page
        browser.close()


def test_homepage_elements(page):
    page.goto("http://localhost:8000/ui")

    assert "AI-Tomator" in page.query_selector("aside").inner_html()


