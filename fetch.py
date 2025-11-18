from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import re
from config import URL, BASE_URL
from urllib.parse import urljoin


def get_html(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_load_state('networkidle') 
        html = page.content()
        browser.close()
        return html
    

def get_img(html):
    images = []
    soup = BeautifulSoup(html, "lxml")

    hero = soup.find("div", class_="hero-background")
    if hero:
        style_or_data = hero.get("data-backgroundimage") or hero.get("style", "")
        match = re.search(r"url\((.*?)\)", style_or_data)
        if match:
            img_url = match.group(1).strip("'\"")
            if not img_url.endswith("lazy.svg"):
                images.append(urljoin(BASE_URL, img_url))

    img_tags = soup.find_all("img")
    for img in img_tags:
        src = (
            img.get("data-src")
            or img.get("data-original")
            or img.get("data-lazy")
            or img.get("src")
        )

        if not src or src.endswith("lazy.svg"):
            continue

        src = re.sub(r"_lazy(\.\w+)$", r"\1", src)

        images.append(urljoin(BASE_URL, src))

    figures = soup.find_all("figure", class_="image progressive replace")
    for fig in figures:
        data_href = fig.get("data-href")
        if data_href:
            images.append(urljoin(BASE_URL, data_href))

    return list(dict.fromkeys(images))


# print(get_html(URL))
# print(get_img(get_html(URL)))