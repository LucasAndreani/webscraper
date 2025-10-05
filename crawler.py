from playwright.sync_api import sync_playwright
import time
from config import BASE


def get_links(base, start_page=1, end_page=2):
    LINKS = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        for i in range(start_page, end_page):
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
    return f"Total de noticias encontradas: \n{LINKS}"


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

print(get_links(BASE, 1, 3))