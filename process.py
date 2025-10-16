from fetch import get_html, get_img
from bs4 import BeautifulSoup
from config import URL, BASE_URL
from urllib.parse import urljoin
import re
import requests
import os
import json
from markdownify import MarkdownConverter, markdownify as md

class MantenerEmbedsConverter(MarkdownConverter):
    def convert_div(self, el, text, convert_as_inline=False, **kwargs):
        if el.find(["iframe", "blockquote", "script"]):
            return str(el)
        try:
            return super().convert_div(el, text, convert_as_inline=convert_as_inline, **kwargs)
        except TypeError:
            return super().convert_div(el, text, **kwargs)

    def convert_iframe(self, el, text, convert_as_inline=False, **kwargs):
        return str(el)

    def convert_blockquote(self, el, text, convert_as_inline=False, **kwargs):
        return str(el)
    
    def convert_script(self, el, text, convert_as_inline=False, **kwargs):
        src = el.get("src", "")
        if "instagram" in src:
            return str(el)
        return "" 
    
    def convert_p(self, el, text, convert_as_inline=False, **kwargs):
        a_tag = el.find("a", href=True)
        if (
            a_tag
            and "youtube.com" in a_tag["href"]
            and a_tag.find("img")
            and len(el.find_all(recursive=False)) == 1  
        ):
            return str(el)
        try:
            return super().convert_p(el, text, convert_as_inline=convert_as_inline, **kwargs)
        except TypeError:
            return super().convert_p(el, text, **kwargs)



def to_markdown(html): 
    soup = BeautifulSoup(html, "lxml")
    content = soup.find("section", class_="container module-content")
    hero = soup.find("div", class_="hero-background")
    if not content:
        raise Exception('Contenido no encontrado')

    hero_url = ""
    if hero:
        hero_str = str(hero)
        match = re.search(r'url\((.*?)\)', hero_str)
        if match:
            hero_url = match.group(1).strip("'\"")
    if not hero_url:
        raise Exception("Imagen hero no encontrada")

    converter = MantenerEmbedsConverter()
    body = converter.convert(str(content)).strip()

    
    markdown_convertido = f"![]({hero_url})\n\n{body}"

    matches = re.findall(r'\((/[^)]+)\)', markdown_convertido)
    for match in matches:
        full_url = urljoin(BASE_URL, match)  
        markdown_convertido = markdown_convertido.replace(match, full_url)
    
    return markdown_convertido
      
    
def write_img(images, URL): 
    os.makedirs("images/noticias", exist_ok=True)
    nombre_base = os.path.basename(URL.rstrip("/"))
    replacements = {}

    for i, img in enumerate(images, start=1):
        try:
            response = requests.get(img, timeout=10)
            if response.status_code == 200:
                ext = os.path.splitext(img)[1] or ".jpg"
                if i == 1:
                    file = f"{nombre_base}{ext}"
                else:
                    file = f"{nombre_base}_{i - 1}{ext}"

                path = os.path.join("images/noticias", file)
                with open(path, "wb") as f:
                    f.write(response.content)

                replacements[img] = f"https://davinci.edu.ar/uploads/images/noticias/{file}"

            else:
                print(f"Error descargando: {img}")
        except Exception as e:
            print(f"Error descargando {img}: {e}")

    return replacements


def write_md(markdown, URL, tags): 
    os.makedirs("md/noticias", exist_ok=True)
    file_md = os.path.basename(URL.rstrip("/")) + ".md"
    path_md = os.path.join("md/noticias", file_md)
    with open(path_md, "w", encoding="utf-8") as f:
        f.write(markdown)
    print(f"Escrita: {file_md}")

    data = {
        "content": markdown,
        "labels": tags
    }

    os.makedirs("json/noticias", exist_ok=True)
    file_json = os.path.basename(URL.rstrip("/")) + ".json"
    path_json = os.path.join("json/noticias", file_json)
    with open(path_json, "w") as j:
        json.dump(data, j, ensure_ascii=False, indent=2)
    print(f"Escrita: {file_json}")


def get_tags(html):
    soup = BeautifulSoup(html, 'lxml')
    content = soup.find("section", class_="container-fluid module-tags")
    tags = [a['href'].removeprefix('/noticias/etiquetas/') for a in content.find_all('a', href=True)]
    return tags[:-1]
    

def rewrite_image(markdown, replacements):
    for old_url, new_url in replacements.items():
        markdown = markdown.replace(old_url, new_url)
    return markdown


# print(to_markdown(get_html(URL)))

print(get_tags(get_html(URL)))