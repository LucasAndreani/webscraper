from playwright.sync_api import sync_playwright
from config import URL

def get_html(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_load_state('networkidle')
        html = page.content()
        browser.close()
        return html

print(get_html(URL))