from fetch import get_html, get_img
from bs4 import BeautifulSoup
from config import URL
import re
import requests
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
    
def write_img():
    images = get_img(URL)
    for img in images:
        data = requests.get(img).content


print(to_markdown(get_html(URL)))