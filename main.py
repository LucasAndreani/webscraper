from fetch import get_html, get_img
from crawler import get_links
from process import to_markdown, write_img, write_md, get_tags, rewrite_image
from config import BASE, URL
from playwright.sync_api import TimeoutError



def main():
    links = get_links(BASE, 1, 36)  

    for link in links:
        retries = 3
        for attempt in range(1, retries + 1):
            try:
                html = get_html(link)
                break 
            except TimeoutError:
                print(f"Timeout en el intento {attempt} para {link}. Reintentando...")
        else:
            print(f"Error obteniendo {link} luego de {retries} intentos. Salteando.")
            continue

        images = get_img(html)
        replacements = write_img(images, link)
        markdown_converted = to_markdown(html)
        tags = get_tags(markdown_converted)
        write_md(rewrite_image(markdown_converted, replacements), link, tags)


        

main()