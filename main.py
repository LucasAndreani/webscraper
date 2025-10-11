from fetch import get_html, get_img
from crawler import get_links
from process import to_markdown, write_img, write_md
from config import BASE


def main():
    links = get_links(BASE, 1, 36)
    for link in links:
        html = get_html(link)
        images = get_img(html)
        write_img(images)
        markdown_converted = to_markdown(html)
        write_md(markdown_converted)
        


        

