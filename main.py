import time
from fetch import get_html, get_img
from crawler import get_links, get_paginated_html, get_cursos_links
from process import eventos_to_markdown, write_img, write_noticias_md, get_tags, rewrite_image, write_titles, write_eventos_md, get_titles_time_data, cursos_to_data, write_cursos
from config import NOTICIAS_BASE, EVENTOS_BASE, URL, EVENTOS_LINKS, CURSOS_LINKS, CURSOS
from playwright.sync_api import TimeoutError



def main():
    for curso in []:
        write_cursos(cursos_to_data(curso, get_html(curso)))
    # get_cursos_links(CURSOS_LINKS)

#     links = [
# ]
#     for link in links:
#         retries = 3
#         for attempt in range(1, retries + 1):
#             try:
#                 html = get_html(link)
#                 break 
#             except TimeoutError:
#                 print(f"Timeout en el intento {attempt} para {link}. Reintentando...")
#         else:
#             print(f"Error obteniendo {link} luego de {retries} intentos. Salteando.")
#             continue

#         images = get_img(html)
#         data = get_titles_time_data(html)
#         replacements = write_img(images, link, "eventos")
#         markdown_converted = eventos_to_markdown(html)
#         write_eventos_md(rewrite_image(markdown_converted, replacements), link, data)
#         time.sleep(0.3)

    # write_titles(get_paginated_html(EVENTOS_BASE, 1, 198), 'eventos')
    # write_titles(get_paginated_html(NOTICIAS_BASE, 1, 35), 'noticias')


        
if __name__ == "__main__":
    main()
