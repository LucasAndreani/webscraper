from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
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
    

def get_img(html):
    images = []
    soup = BeautifulSoup(html, 'lxml')
    hero_div = soup.find('div', class_='hero-background')

    

    img_tag = soup.find_all('img')
    for img in img_tag: 
        images.append(img.get('src'))

    return images


# print(get_html(URL))
# print(get_img(get_html(URL)))