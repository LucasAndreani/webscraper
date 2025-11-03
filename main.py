import time
from fetch import get_html, get_img
from crawler import get_links, get_paginated_html
from process import eventos_to_markdown, write_img, write_noticias_md, get_tags, rewrite_image, write_titles, write_eventos_md, get_titles_time_data
from config import NOTICIAS_BASE, EVENTOS_BASE, URL, EVENTOS_LINKS
from playwright.sync_api import TimeoutError



def main():
    links = [
    "https://davinci.edu.ar/eventos/detalle/experiencia-da-vinci-un-evento-para-volarle-la-cabeza-al-artista-independiente",
    "https://davinci.edu.ar/eventos/detalle/experiencia-da-vinci-un-mega-evento-para-el-artista-independiente2017",
    "https://davinci.edu.ar/eventos/detalle/conferencia-gratuita-secretos-ocultos-del-photoshop-2015",
    "https://davinci.edu.ar/eventos/detalle/experiencia-videojuego-desarrollamos-un-videojuego-en-vivo",
    "https://davinci.edu.ar/eventos/detalle/hearthstone-tavern-hero-buenos-aires",
    "https://davinci.edu.ar/eventos/detalle/conferencia-gratuita-por-donde-empiezo-mi-primer-videojuegobaht",
    "https://davinci.edu.ar/eventos/detalle/masterclass-online-de-marketing-digital-como-lograr-que-tus-clientes-se-enamoren-de-tu-marca",
    "https://davinci.edu.ar/eventos/detalle/experiencia-da-vinci-ilustracion-y-comics-12-08-2023",
    "https://davinci.edu.ar/eventos/detalle/masterclass-online-de-ilustracion-artistica-digital-como-hacer-la-miniatura-de-un-fondo",
    "https://davinci.edu.ar/eventos/detalle/masterclass-online-de-diseno-grafico-como-crear-una-historia-animada-para-redes-sociales2",
    "https://davinci.edu.ar/eventos/detalle/serie-de-clases-abiertas-para-emprendedores",
    "https://davinci.edu.ar/eventos/detalle/masterclass-online-de-ilustracion-artistica-digital-realizacion-de-concept-art",
    "https://davinci.edu.ar/eventos/detalle/masterclass-online-de-diseno-grafico-digital-creacion-de-afiche-publicitario",
    "https://davinci.edu.ar/eventos/detalle/conferencia-gratuita-como-animar-con-maya",
    "https://davinci.edu.ar/eventos/detalle/masterclass-de-arte-para-videojuegos-diseno-de-un-personaje-fondos-e-interfaz-de-un-videojuego-2d",
    "https://davinci.edu.ar/eventos/detalle/masterclass-online-de-ilustracion-artistica-digital-diseno-y-proceso-de-creacion-de-fondos",
    "https://davinci.edu.ar/eventos/detalle/muestra-de-diseno-web-y-analista-de-sistemas-primero-los-primeros",
    "https://davinci.edu.ar/eventos/detalle/presentaci-n-del-libro-memoria-del-juego-dise-o-de-juegos-en-am-rica-latina-parte-3",
    "https://davinci.edu.ar/eventos/detalle/dia-internacional-de-la-animacion-conferencias-y-proyecciones",
    "https://davinci.edu.ar/eventos/detalle/clases-gratuitas-para-emprendedores-como-crear-tu-ecosistema-digital",
    "https://davinci.edu.ar/eventos/detalle/masterclass-de-marketing-ecommerce-y-sus-estrategias-de-venta-digitales",
    "https://davinci.edu.ar/eventos/detalle/masterclass-como-disciplinar-la-creatividad",
    "https://davinci.edu.ar/eventos/detalle/conferencia-gratuita-el-gran-ilustrador-augusto-costhanzo-recorre-su-trabajo",
    "https://davinci.edu.ar/eventos/detalle/masterclass-online-de-diseno-grafico-digital-como-hacer-un-logotipo",
    "https://davinci.edu.ar/eventos/detalle/clase-gratuita-para-chicos-realizacion-de-videojuego-2d-estilo-top-down-shooter",
    "https://davinci.edu.ar/eventos/detalle/como-desarrollar-un-proyecto-independiente-sin-morir-en-el-intento-con-martin-garabal",
    "https://davinci.edu.ar/eventos/detalle/masterclass-online-de-diseno-grafico-digital-aprende-a-crear-tu-logotipo-con-illustrator-encore",
    "https://davinci.edu.ar/eventos/detalle/masterclass-online-de-diseno-grafico-como-disenar-stories-animadas-para-redes-sociales",
    "https://davinci.edu.ar/eventos/detalle/masterclass-online-de-comics-como-crear-heroes-y-villanos",
    "https://davinci.edu.ar/eventos/detalle/clases-gratuitas-para-emprendedores-como-armar-un-website-efectivo",
    "https://davinci.edu.ar/eventos/detalle/masterclass-online-de-escultura-digital-con-zbrush-y-marvelous-designer",
    "https://davinci.edu.ar/eventos/detalle/herramientas-para-la-busqueda-laboral-desde-una-vision-emprendedora",
    "https://davinci.edu.ar/eventos/detalle/conferencia-gratuita-rene-castillo-aventuras-y-vicisitudes-de-un-animador-latinoamericano",
    "https://davinci.edu.ar/eventos/detalle/masterclass-online-de-ilustracion-de-dragones",
    "https://davinci.edu.ar/eventos/detalle/masterclass-de-diseno-web-como-generar-un-e-commerce-con-wordpress",
    "https://davinci.edu.ar/eventos/detalle/masterclass-de-diseno-web-como-generar-un-e-commerce-exitoso",
    "https://davinci.edu.ar/eventos/detalle/conferencia-gratuita-secretos-ocultos-del-photoshop01",
    "https://davinci.edu.ar/eventos/detalle/torneo-de-major-cs-go-temporada-de-juegos-2017-en-escuela-da-vinci",
    "https://davinci.edu.ar/eventos/detalle/clases-gratuitas-para-emprendedores-como-armar-un-logotipo",
    "https://davinci.edu.ar/eventos/detalle/clase-abierta-diseno-creativo-y-realizacion-de-porfolio2",
    "https://davinci.edu.ar/eventos/detalle/masterclass-modelado-3d-con-3ds-max-de-objeto-con-acabado-fotorrealista",
    "https://davinci.edu.ar/eventos/detalle/masterclass-online-de-diseno-web-como-generar-un-sitio-de-venta-online",
    "https://davinci.edu.ar/eventos/detalle/conferencia-gratuita-comics-como-se-crea-un-personaje-presentacion-de-jellykid-2",
    "https://davinci.edu.ar/eventos/detalle/conferencia-gratuita-introduccion-al-photoshop-avanzado",
    "https://davinci.edu.ar/eventos/detalle/masterclass-online-de-modelado-3d-de-un-exterior-arquitectonico-con-3ds-max",
    "https://davinci.edu.ar/eventos/detalle/conferencia-gratuita-tecnicas-de-modelado-con-3d-max-y-maya",
    "https://davinci.edu.ar/eventos/detalle/globant-a-game-developer-toolbox",
    "https://davinci.edu.ar/eventos/detalle/muestra-de-arte-digital-de-diseno-y-desarrollo-de-videojuegos-primero-los-primeros",
    "https://davinci.edu.ar/eventos/detalle/conferencia-gratuita-ilustracion-profesional-del-boceto-al-cuadro-terminado",
    "https://davinci.edu.ar/eventos/detalle/conferencia-gratuita-diseno-de-infografias-algo-mas-que-dibujitos",
    "https://davinci.edu.ar/eventos/detalle/bit-bang-fest-videojuegos-segunda-edicion",
    "https://davinci.edu.ar/eventos/detalle/taller-gratuito-de-game-design-arte-y-prototipado-digital-con-construct-2",
    "https://davinci.edu.ar/eventos/detalle/conferencia-gratuita-secretos-ocultos-del-photoshop3",
    "https://davinci.edu.ar/eventos/detalle/gran-berta-como-aprovechar-las-redes-al-maximo",
    "https://davinci.edu.ar/eventos/detalle/conferencia-gratuita-y-demostracion-en-vivo-la-pintura-en-la-era-digital-10-05-2014",
    "https://davinci.edu.ar/eventos/detalle/clase-online-render-y-vfx-para-animacion-3d",
    "https://davinci.edu.ar/eventos/detalle/conferencia-gratuita-y-demostracion-en-vivo-la-pintura-en-la-era-digital",
    "https://davinci.edu.ar/eventos/detalle/masterclass-online-de-diseno-grafico-digital-crea-un-afiche-publicitario-con-photoshop-encore",
    "https://davinci.edu.ar/eventos/detalle/clases-gratuitas-para-emprendedores-arma-tu-propio-negocio",
    "https://davinci.edu.ar/eventos/detalle/conferencia-gratuita-tips-del-creador-de-preguntados",
    "https://davinci.edu.ar/eventos/detalle/conferencia-gratuita-secretos-ocultos-del-photoshop4",
    "https://davinci.edu.ar/eventos/detalle/concurso-de-videos-tik-tok-challenge",
    "https://davinci.edu.ar/eventos/detalle/masterclass-online-hace-un-videojuego-2d-con-nosotros",
    "https://davinci.edu.ar/eventos/detalle/conferencia-gratuita-la-liga-de-la-justicia-publicitaria-el-poder-de-las-buenas-ideas",
    "https://davinci.edu.ar/eventos/detalle/conferencia-gratuita-desarrollo-de-videojuegos-aaa-de-alta-calidad-en-argentina",
    "https://davinci.edu.ar/eventos/detalle/taller-gratuito-de-game-design-dise-ando-un-esport",
    "https://davinci.edu.ar/eventos/detalle/conferencia-gratuita-diseno-grafico-seamos-libros-que-lo-demas-no-importa-nada",
    "https://davinci.edu.ar/eventos/detalle/conferencia-gratuita-lumbretv-muestra-el-mejor-motion-graphics-de-argentina",
    "https://davinci.edu.ar/eventos/detalle/clase-online-disenamos-un-videojuego-en-vivo",
    "https://davinci.edu.ar/eventos/detalle/da-vinci-forma-muestra-de-multimedia-cine-de-animacion-desarrollo-web",
    "https://davinci.edu.ar/eventos/detalle/masterclass-online-de-escultura-digital-con-zbrush",
    "https://davinci.edu.ar/eventos/detalle/masterclass-online-de-motion-graphics-tracking-y-magia-con-after-effects",
    "https://davinci.edu.ar/eventos/detalle/muestra-de-diseno-multimedia-y-animacion-da-vinci-2015",
    "https://davinci.edu.ar/eventos/detalle/conferencias-gratuitas-nelson-luty-warner-marvel-comics-mauro-serei-sony-pictures-angry-birds",
    "https://davinci.edu.ar/eventos/detalle/masterclass-online-de-diseno-de-criaturas-y-personajes-fantasticos",
    "https://davinci.edu.ar/eventos/detalle/clase-gratuita-de-ilustracion-para-chicos-dibujo-de-personajes-humanos-y-pintura-digital",
    "https://davinci.edu.ar/eventos/detalle/masterclass-modelado-3d-con-3ds-max-de-un-interior-fotorrealista",
    "https://davinci.edu.ar/eventos/detalle/conferencia-gratuita-2veinte-una-mirada-interna-al-motion-graphics-industria-en-pleno-crecimiento"
]
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
        data = get_titles_time_data(html)
        replacements = write_img(images, link, "eventos")
        markdown_converted = eventos_to_markdown(html)
        write_eventos_md(rewrite_image(markdown_converted, replacements), link, data)
        time.sleep(0.3)

    # write_titles(get_paginated_html(EVENTOS_BASE, 1, 198), 'eventos')
    # write_titles(get_paginated_html(NOTICIAS_BASE, 1, 35), 'noticias')


        
if __name__ == "__main__":
    main()
