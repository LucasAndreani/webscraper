from playwright.sync_api import sync_playwright
import time
from fetch import get_html
from process import write_titles
from bs4 import BeautifulSoup
import re


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


def get_cursos_links(cursos_links):
    LINKS = []

    with sync_playwright() as p:
        for link in cursos_links:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            print(f"Visitando: {link}")
            page.goto(link, timeout=60000)
            page.wait_for_load_state("networkidle")
            
            cursos = page.eval_on_selector_all("a", "elements => elements.map(a => a.href)")
            cursos_counter = 0
            
            for href in cursos:
                if '/cursos' in href and href not in LINKS:
                    LINKS.append(href)
                    cursos_counter += 1
            print(f"Se encontraron {cursos_counter} cursos en la página {link}")
        
            browser.close()  
            time.sleep(0.1)
    print(f"Total de cursos encontrados: \n{LINKS}")
    return LINKS


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


def parse_courses_pages(urls):
    data = []

    color_map = {
        "Diseño Gráfico": "purple",
        "Marketing Digital y Desarrollo Web": "lightblue",
        "Videojuegos y Arte 3D": "red",
        "Edición de Video y Cine Digital": "blue",
        "Ilustración y Comics": "violet",
        "Fotografía": "jade",
        "Cursos de Ilustración e Historietas": "violet"
    }

    icon_map = {
        "purple": "https://davinci.edu.ar/uploads/images/icons/design.svg",
        "lightblue": "https://davinci.edu.ar/uploads/images/icons/web.svg",
        "red": "https://davinci.edu.ar/uploads/images/icons/3d.svg",
        "blue": "https://davinci.edu.ar/uploads/images/icons/video.svg",
        "violet": "https://davinci.edu.ar/uploads/images/icons/paintbrush.svg",
        "jade": "https://davinci.edu.ar/uploads/images/icons/camera.svg",
        "green": "https://davinci.edu.ar/uploads/images/icons/helmet.svg"
    }

    for url in urls:
        try:
            html = get_html(url)
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            continue

        soup = BeautifulSoup(html, "lxml")

        for section in soup.select("article.course-list-orientation"):
            title_tag = section.select_one("h1")
            if not title_tag:
                continue
            section_title = title_tag.get_text(strip=True)

            color = color_map.get(section_title, "green")

            items = []
            for li in section.select("li.item"):
                a_tag = li.select_one("a[href]")
                text_block = li.select_one("article.text")

                course_title = text_block.select_one("h1").get_text(strip=True) if text_block else ""
                type_p = text_block.select_one("p.type")
                desc_p = None
                tag_p = None

                for p in text_block.select("p"):
                    if "type" not in p.get("class", []) and "highlight" not in p.get("class", []):
                        desc_p = p
                    elif "highlight" in p.get("class", []):
                        tag_p = p

                subtitle = ""
                hours = ""
                if type_p:
                    match = re.search(r"(\d+)\s*hs", type_p.get_text())
                    hours = int(match.group(1)) if match else None
                    subtitle = re.sub(r"-?\s*\d+\s*hs\.?", "", type_p.get_text()).strip(" -")

                tag_text = tag_p.get_text(strip=True) if tag_p else ""
                tag_type = "recommended"
                if re.search(r"básico", tag_text, re.I):
                    tag_type = "basic"
                elif re.search(r"alta demanda", tag_text, re.I):
                    tag_type = "high_demand"
                elif re.search(r"especialización", tag_text, re.I):
                    tag_type = "specialization"
                elif re.search(r"nuevo", tag_text, re.I):
                    tag_type = "new"

                icon_path = icon_map.get(color, "")

                course_url = ""
                if a_tag:
                    href = a_tag.get("href", "")
                    course_url = href.rstrip("/").split("/")[-1]

                items.append({
                    "title": course_title,
                    "subtitle": subtitle,
                    "color": color,
                    "hours": hours,
                    "description": desc_p.get_text(strip=True) if desc_p else "",
                    "tag": {
                        "text": tag_text,
                        "type": tag_type
                    },
                    "url": course_url,
                    "icon_path": icon_path
                })

            data.append({
                "section_title": section_title,
                "items": items
            })

        time.sleep(0.2)

    return data




# check_status(BASE)

# print(get_links(BASE, 1, 3))

# write_titles(parse_courses_pages(['https://davinci.edu.ar/cursos/online']), 'online')