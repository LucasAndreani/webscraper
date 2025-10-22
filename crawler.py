from playwright.sync_api import sync_playwright
import time
from fetch import get_html
from bs4 import BeautifulSoup


def get_links(base, start_page=1, end_page=2):
    LINKS = []
    with sync_playwright() as p:
        for i in range(start_page, end_page + 1):
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            url = f"{base}{i}"
            print(f"Visitando: {url}")
            page.goto(url, timeout=60000)
            page.wait_for_load_state("networkidle")
            
            noticias = page.eval_on_selector_all("a", "elements => elements.map(a => a.href)")
            noticias_counter = 0
            
            for href in noticias:
                if '/detalle' in href and href not in LINKS:
                    LINKS.append(href)
                    noticias_counter += 1
            print(f"Se encontraron {noticias_counter} noticias en la página {i}")
        
            browser.close()  
            time.sleep(0.1)
    print(f"Total de noticias encontradas: \n{LINKS}")
    return LINKS


def get_paginated_html(base, start_page=1, end_page=2):
    data = []
    
    for i in range (start_page, end_page + 1):
        url = f'{base}{i}'
        try:
            html = get_html(url)
        except Exception as e:
            print(f"Error obteniendo el html de {url}: {e}")

        soup = BeautifulSoup(html, 'lxml')

        for li in soup.select("li.snippet.boxed"):
            a_tag = li.select_one("a[href]")
            title = li.select_one("h2")
            subtitle = li.select_one("p.subtitle")
            desc_p = li.select_one("article.text p:not(.subtitle)")

            url_end = ""
            if a_tag:
                href = a_tag.get("href", "")
                url_end = href.rstrip("/").split("/")[-1]
        
            data.append({
                "url": url_end,
                "title": title.get_text(strip=True) if title else "",
                "subtitle": subtitle.get_text(strip=True) if subtitle else "",
                "description": desc_p.get_text(strip=True) if desc_p else ""
            })

        time.sleep(0.1)

    return data


def check_status(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        response = page.goto(url, timeout=60000)
        html = page.content()
        print(f"Status code: {response.status}")
        time.sleep(2)
        print(html)
        browser.close()

# check_status(BASE)

# print(get_links(BASE, 1, 3))