import os
from playwright.sync_api import sync_playwright

BASE_URL = os.getenv("BASE_URL", "http://localhost:3000")
SEARCH_PATH = "/search"
RADIO_LABEL = "Yesterday"
SEARCH_BUTTON_SELECTOR = '[data-test="search-btn"], button[type="submit"]'
RESULT_ITEMS_SELECTOR = '[data-test="result-item"], ul.results > li, .result-item'

def test_yesterday_search_print_results():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(BASE_URL + SEARCH_PATH, wait_until="domcontentloaded")

        try:
            page.get_by_label(RADIO_LABEL).check()
        except Exception:
            page.check('input[type="radio"][value="yesterday"], [data-test="radio-yesterday"]')

        page.wait_for_timeout(150)
        page.click(SEARCH_BUTTON_SELECTOR)

        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(300)

        items = page.locator(RESULT_ITEMS_SELECTOR)
        count = items.count()
        print(f"\n=== Yesterday arama sonucu: {count} kayıt ===")
        for i in range(count):
            el = items.nth(i)
            title = el.locator("h3, h4, .title, [data-test='title']").first
            text = title.inner_text() if title.count() else el.inner_text()[:120]
            print(f"{i+1}. {text.strip()}")

        browser.close()