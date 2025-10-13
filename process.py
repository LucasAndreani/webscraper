from fetch import get_html, get_img
from bs4 import BeautifulSoup
from config import URL
import re
import requests
import os
from markdownify import MarkdownConverter, markdownify as md

class MantenerEmbedsConverter(MarkdownConverter):
    def convert_div(self, el, text, convert_as_inline=False, **kwargs):
        if el.find(["iframe", "blockquote", "script"]):
            return str(el)
        return super().convert_div(el, text, convert_as_inline=convert_as_inline, **kwargs)

    def convert_iframe(self, el, text, convert_as_inline=False, **kwargs):
        return str(el)

    def convert_blockquote(self, el, text, convert_as_inline=False, **kwargs):
        return str(el)
    
    def convert_script(self, el, text, convert_as_inline=False, **kwargs):
        src = el.get("src", "")
        if "instagram" in src:
            return str(el)
        return "" 

def to_markdown(html):
    soup = BeautifulSoup(html, "lxml")
    content = soup.find("section", class_="container module-content")
    hero = soup.find("div", class_="hero-background")
    if not content:
        return ""

    hero_url = ""
    if hero:
        hero_str = str(hero)
        match = re.search(r'url\((.*?)\)', hero_str)
        if match:
            hero_url = match.group(1).strip("'\"")

    converter = MantenerEmbedsConverter()
    body = converter.convert(str(content)).strip()

    if hero_url:
        return f"![]({hero_url})\n\n{body}"
    else:
        return body
    
def write_img(images, URL):
    os.makedirs("images/noticias", exist_ok=True)
    nombre_base = os.path.basename(URL.rstrip("/"))

    for i, img in enumerate(images, start=1):
        try:
            response = requests.get(img, timeout=10)
            if response.status_code == 200:
                ext = os.path.splitext(img)[1] or ".jpg"
                if len(images) == 1:
                    file = f"{nombre_base}{ext}"
                else:
                    file = f"{nombre_base}_{i}{ext}"

                path = os.path.join("images/noticias", file)
                with open(path, "wb") as f:
                    f.write(response.content)
            else:
                print(f"Error descargando: {img}")
        except Exception as e:
            print(f"Error descargando {img}: {e}")



def write_md(markdown, URL):
    os.makedirs("md/noticias", exist_ok=True)
    file = os.path.basename(URL.rstrip("/")) + ".md"
    path = os.path.join("md/noticias", file)
    with open(path, "w", encoding="utf-8") as f:
        f.write(markdown)
    print(f"Escrita: {file}")



# print(to_markdown(get_html(URL)))