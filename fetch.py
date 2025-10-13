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
    soup = BeautifulSoup(html, 'lxml')
    hero = soup.find("div", class_="hero-background")
    if hero:
        hero_str = str(hero)
        match = re.search(r'url\((.*?)\)', hero_str)
        if match:
            img_url = match.group(1).strip("'\"")
            images.append(urljoin(BASE_URL, img_url))

    img_tag = soup.find_all('img')
    for img in img_tag:
        src = img.get('src')
        if src:
            images.append(urljoin(BASE_URL, src))


    return images


# print(get_html(URL))
# print(get_img(get_html(URL)))