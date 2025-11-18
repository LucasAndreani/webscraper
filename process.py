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



def noticias_to_markdown(html): 
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


def eventos_to_markdown(html): 
    soup = BeautifulSoup(html, "lxml")
    content = soup.find("section", class_="container module-content event-description no-padding-top")
    if not content:
        raise Exception('Contenido no encontrado')

    converter = MantenerEmbedsConverter()
    markdown_convertido = converter.convert(str(content)).strip()


    matches = re.findall(r'\((/[^)]+)\)', markdown_convertido)
    for match in matches:
        full_url = urljoin(BASE_URL, match)  
        markdown_convertido = markdown_convertido.replace(match, full_url)
    
    return markdown_convertido
      
    
def write_img(images, URL, path): 
    folder = os.path.join("images", path)
    os.makedirs(folder, exist_ok=True)

    nombre_base = os.path.basename(URL.rstrip("/"))
    nombre_base, ext_existente = os.path.splitext(nombre_base)  
    replacements = {}

    for i, img in enumerate(images, start=1):
        try:
            response = requests.get(img, timeout=10)
            if response.status_code == 200:
                ext = ext_existente or os.path.splitext(img)[1] or ".jpg"

                if i == 1:
                    file = f"{nombre_base}{ext}"
                else:
                    file = f"{nombre_base}_{i - 1}{ext}"

                file_path = os.path.join(folder, file)
                with open(file_path, "wb") as f:
                    f.write(response.content)

                replacements[img] = f"https://davinci.edu.ar/uploads/images/{path}/{file}"

            else:
                print(f"Error descargando: {img}")
        except Exception as e:
            print(f"Error descargando {img}: {e}")

    return replacements



def write_noticias_md(markdown, URL, tags): 
    markdown = remove_etiquetas(markdown)

    os.makedirs("md/noticias", exist_ok=True)
    file_md = os.path.basename(URL.rstrip("/")) + ".md"
    path_md = os.path.join("md/noticias", file_md)
    with open(path_md, "w", encoding="utf-8") as f:
        f.write(markdown)

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


def write_eventos_md(markdown, URL, titles_time_data): 

    os.makedirs("md/eventos", exist_ok=True)
    file_md = os.path.basename(URL.rstrip("/")) + ".md"
    path_md = os.path.join("md/eventos", file_md)
    with open(path_md, "w", encoding="utf-8") as f:
        f.write(markdown)
    print(f"Escrita: {file_md}")

    data = {
        "title": titles_time_data['title'],
        "subtitle": titles_time_data['subtitle'],
        "description": titles_time_data['description'],
        "day": titles_time_data['dia'],
        "hour": titles_time_data['hora'],
        "place": titles_time_data['lugar'],
        "content": markdown,
    }

    os.makedirs("json/eventos", exist_ok=True)
    file_json = os.path.basename(URL.rstrip("/")) + ".json"
    path_json = os.path.join("json/eventos", file_json)
    with open(path_json, "w") as j:
        json.dump(data, j, ensure_ascii=False, indent=2)
    print(f"Escrita: {file_json}")


def get_tags(markdown):
    matches = re.findall(r'\[.*?\]\(https://davinci\.edu\.ar/noticias/etiquetas/([^)]+)\)', markdown)
    return matches


def get_titles_time_data(html):
    soup = BeautifulSoup(html, "lxml")
    data = {}

    content_section = soup.find("section", class_="container module-content half-padding-bottom")
    if content_section:
        data["title"] = (content_section.find("h1").get_text(strip=True)
                         if content_section.find("h1") else "")
        data["subtitle"] = (content_section.find("h2").get_text(strip=True)
                            if content_section.find("h2") else "")
        data["description"] = (content_section.find("p").get_text(strip=True)
                               if content_section.find("p") else "")

    aside = soup.find("aside", class_="container module-info-strip")
    if aside:
        text = aside.get_text(" ", strip=True)

        dia_match = re.search(r"Dí?a?s?:\s*(.*?)\s*(?:Horario:|$)", text, re.IGNORECASE)
        hora_match = re.search(r"Horario:\s*(.*?)\s*(?:Lugar:|$)", text, re.IGNORECASE)
        lugar_match = re.search(r"Lugar:\s*(.*)", text, re.IGNORECASE)

        data["dia"] = dia_match.group(1).strip() if dia_match else "No disponible"
        data["hora"] = hora_match.group(1).strip() if hora_match else "No disponible"
        data["lugar"] = lugar_match.group(1).strip() if lugar_match else "No disponible"

    return data
    

def rewrite_image(markdown, replacements):
    for old_url, new_url in replacements.items():
        markdown = markdown.replace(old_url, new_url)
    return markdown


def remove_etiquetas(markdown):
    lines = markdown.splitlines()
    new_lines = []
    for line in lines:
        if line.strip().startswith("Etiquetas:"):
            break
        new_lines.append(line)
    return "\n".join(new_lines)


def write_titles(data, path):
    os.makedirs(f"titles_json/cursos", exist_ok=True)
    with open(f"titles_json/cursos/cursos_{path}.json", "w", encoding="utf-8") as j:
        json.dump(data, j, ensure_ascii=False, indent=2)

def already_exists(data, new_blocks):
    
    if not new_blocks:
        return False

    existing_pairs = set()
    for group in data.get("content", []):
        if isinstance(group, list):
            for block in group:
                if isinstance(block, dict):
                    tpl = block.get("template", "").strip() if block.get("template") else ""
                    title = block.get("title", "").strip() if block.get("title") else ""
                    existing_pairs.add((tpl, title))
        elif isinstance(group, dict):
            tpl = group.get("template", "").strip() if group.get("template") else ""
            title = group.get("title", "").strip() if group.get("title") else ""
            existing_pairs.add((tpl, title))

    for block in new_blocks:
        if not isinstance(block, dict):
            continue
        tpl = block.get("template", "").strip() if block.get("template") else ""
        title = block.get("title", "").strip() if block.get("title") else ""
        if (tpl, title) in existing_pairs:
            return True

    return False

def append_unique(data, key, parsed):
    if not parsed:
        return
    
    blocks = parsed if isinstance(parsed, list) else [parsed]

    if key not in data:
        data[key] = []

    existing_pairs = set()
    for group in data[key]:
        if isinstance(group, list):
            for block in group:
                if isinstance(block, dict):
                    tpl = block.get("template", "").strip()
                    title = block.get("title", "").strip()
                    existing_pairs.add((tpl, title))
        elif isinstance(group, dict):
            tpl = group.get("template", "").strip()
            title = group.get("title", "").strip()
            existing_pairs.add((tpl, title))

    new_clean = []
    for block in blocks:
        if isinstance(block, dict):
            tpl = block.get("template", "").strip()
            title = block.get("title", "").strip()
            if (tpl, title) in existing_pairs:
                continue
        new_clean.append(block)

    if new_clean:
        data[key].append(new_clean)


def cursos_to_data(url, html):
    soup = BeautifulSoup(html, "lxml")

    data = {}

    hero = soup.find("div", class_="hero-background")
    if hero:
        data["banner"] = parse_banner(hero)

    promotion = soup.find("section", class_="container-fluid module-info-highlight narrow")
    if promotion:
        data["promotion"] = parse_promotion(promotion)

    section_contents = soup.find_all("section", class_="container module-content")
    for content in section_contents:
        append_unique(data, "content", parse_content(content))

    section_plain_contents = soup.find_all("section", class_="container")
    for content in section_plain_contents:
        append_unique(data, "content", parse_content(content))

    div_contents = soup.find_all("div", class_="container module-content")
    for content in div_contents:
        append_unique(data, "content", parse_content(content))

    dark_contents = soup.find_all("aside", class_="container module-content no-padding")
    for content in dark_contents:
        append_unique(data, "content", parse_content(content))

    infraestructura = soup.find("section", class_="container module-content no-padding-top")
    if infraestructura:
        append_unique(data, "content", parse_content(infraestructura))

    persons = soup.find("section", class_="container-fluid module-professors")
    if persons:
        data["persons"] = parse_persons(persons)

    work = soup.find("section", class_="container-fluid module-work")
    if work:
        data["company"] = parse_work(work)

    sample_contest = soup.find("section", class_="container-fluid module-video-showcase")
    if sample_contest:
        append_unique(data, "sample_contest", parse_sample_contest(sample_contest))

    news = soup.find("section", class_="container-fluid module-news-showcase")
    if news:
        append_unique(data, "news", parse_news(news))

    horarios = soup.find("section", class_="container-fluid module-schedules")
    if horarios:
        data["schedule"] = parse_horarios(horarios)

    certificate = soup.find("section", class_="container-fluid module-certifications")
    if certificate:
        data["certificate"] = parse_certificate(certificate)

    related_courses = soup.find("section", class_="container-fluid module-related")
    if related_courses:
        data["related_courses"] = parse_related_courses(related_courses)

    productions = soup.find_all(
        "section",
        class_=lambda x: x and "module-showcase" in x
    )

    for prod in productions:
        parsed = parse_production(prod)
        if parsed:  
            data["production"] = parsed
    
    
    page = url.rstrip("/").split("/")[-1]

    results = []
    for key, value in data.items():
        results.append({
            "type": key,
            "data": value
        })

    return {
        "page": page,
        "results": results
    }



def parse_banner(html):
    images = get_img(str(html))
    hgroup = html.find_previous("hgroup", class_="hero-info")
    title = ""
    second_title = ""
    subtitle = ""

    if hgroup:
        h1 = hgroup.find("h1")
        h2 = hgroup.find("h2")

        if h1:
            strong = h1.find("strong")
            if strong:
                title = strong.get_text(strip=True)
                h1_text = h1.get_text(" ", strip=True).replace(title, "").strip(" •")
                second_title = h1_text
            else:
                title = h1.get_text(strip=True)

        if h2:
            subtitle = h2.get_text(strip=True)

    button_color = "yellow"  
    button_text = ""
    button_url = ""
    btn = html.find("a", class_=re.compile(r"btn", re.I))
    if btn:
        button_text = btn.get_text(strip=True)
        button_url = btn.get("href", "")

    image_url = ""
    if images:
        replacements = write_img(images, images[0], "cursos")
        image_url = list(replacements.values())[0]

        return [
    {
        "second_title": second_title,
        "button_color": button_color,
        "button_text": button_text,
        "button_url": button_url,
        "image": image_url,
        "subtitle": subtitle,
        "title": title,
    }
]


def fix_url(u):
    if not u:
        return ""
    u = u.strip().replace("_lazy", "")
    u = u.replace(" ", "")


    if u.startswith("http://") or u.startswith("https://"):
        if "davinci.edu.arhttps" in u:
            u = u.replace("davinci.edu.arhttps", "davinci.edu.ar/")
        return u

    if u.startswith("//"):
        return "https:" + u

    return urljoin(BASE_URL, u)


def parse_content(html):
    h1 = html.find("h1")
    h2 = html.find("h2")
    title_text = (h1.get_text(strip=True) if h1 else "") or (h2.get_text(strip=True) if h2 else "")

    if re.search(r"Infraestructura tecnológica", title_text, re.I):
        ul = html.find("ul")
        items = []
        if ul:
            for li in ul.find_all("li"):
                txt = li.get_text(" ", strip=True)
                if txt:
                    items.append(txt)
        clean_html = "<ul>\n" + "\n".join(f"<li>{i}</li>" for i in items) + "\n</ul>"
        md_text = "\n".join(f"* {i}" for i in items)
        return [
    {
        "template": "infrastructure",
        "title": title_text,
        "html": clean_html,
        "text": md_text,
        "has_infrastructure": True
    }
]

    soup = html
    full_text = soup.get_text(" ", strip=True)

    ignore_patterns = [
        r"Empresas que conf[ií]an en nosotros",
        r"Cada año, Escuela Da Vinci recibe más de\s*1500 ofertas laborales",
        r"Mirá el listado completo de empresas que confian en nosotros",
        r"Coordinación y Profesores",
        r"Muestra y Concurso",
        r"Horarios",
        r"Noticias",
    ]
    for pat in ignore_patterns:
        if re.search(pat, full_text, re.I):
            return

    for img in soup.find_all("img"):
        src = img.get("src", "")
        img["src"] = fix_url(src)

    for a in soup.find_all("a"):
        a["href"] = fix_url(a.get("href", ""))

    for fig in soup.find_all("figure"):
        dh = fig.get("data-href")
        if dh:
            fig["data-href"] = fix_url(dh)

    html_str = str(soup)

    images = get_img(html_str)
    replacements = {}
    if images:
        replacements = write_img(images, images[0], "cursos")

    converter = MantenerEmbedsConverter()
    md_text = converter.convert(html_str).strip()

    for old_url, new_url in replacements.items():
        candidates = set([old_url, urljoin(BASE_URL, old_url), old_url.lstrip(), old_url.replace(" ", "")])
        parsed_rel = re.sub(r"^https?://[^/]+", "", old_url)
        if parsed_rel:
            candidates.add(parsed_rel)
            candidates.add(parsed_rel.lstrip())
        for c in candidates:
            if c:
                html_str = html_str.replace(c, new_url)
                md_text = md_text.replace(c, new_url)

    html_out = html_str.replace("\r\n", "\n")
    text_out = md_text.replace("\n", "\r\n")

    return [
    {
        "template": "text_content",
        "title": title_text,
        "html": html_out,
        "text": text_out,
        "has_text_content": True
    }
]


def parse_promotion(html):
    data_list = []

    for li in html.select("ul.row > li.column"):
        title = ""
        subtitle = ""

        h1 = li.find("h1")
        if h1:
            title = h1.get_text(strip=True)

        p_tags = li.find_all("p")
        if p_tags:
            subtitle_texts = [p.get_text(strip=True) for p in p_tags if title not in p.get_text()]
            subtitle = " ".join(subtitle_texts).strip()

        data_list.append({
            "title": title,
            "subtitle": subtitle
        })

    return data_list

def parse_persons(html):
    persons_list = []

    ul = html.find("ul", class_="slider-professors")
    if not ul:
        return {"type": "persons", "data": []}

    for li in ul.find_all("li", class_="item"):
        h2 = li.find("h2")
        full_name = h2.get_text(strip=True) if h2 else ""
        if " " in full_name:
            parts = full_name.split()
            name = parts[0]
            surname = " ".join(parts[1:])
        else:
            name = full_name
            surname = ""

        degree_tag = li.find("p", class_="speciality")
        degree = degree_tag.get_text(strip=True) if degree_tag else ""

        description_tag = li.find_all("p")
        description = ""
        if description_tag:
            description_texts = []
            for p in description_tag:
                if not p.get("class") or "speciality" not in p.get("class", []):
                    description_texts.append(p.get_text(strip=True))
            description = " ".join(description_texts)

        fig = li.find("figure")
        image_url = ""
        if fig:
            data_href = fig.get("data-href", "")
            if data_href:
                images = get_img(str(fig))
                if images:
                    folder_name = os.path.basename(os.path.dirname(data_href.strip("/")))
                    replacements = write_img(images, folder_name, "professors")
                    image_url = list(replacements.values())[0]

        bio_tag = li.find("a", href=True)
        biography_url = urljoin(BASE_URL, bio_tag["href"]) if bio_tag else ""

        persons_list.append({
            "name": name,
            "surname": surname,
            "degree": degree,
            "description": description,
            "image": image_url,
            "biography_url": biography_url,
            "biography": ""  
        })

    return persons_list

def parse_news(html):
    news_list = []
    ul = html.find("ul", class_="slider-news")
    if not ul:
        return {"type": "news", "data": []}

    for li in ul.find_all("li", class_="slide"):
        a_tag = li.find("a", href=True)
        article = li.find("article", class_="text")
        h2 = article.find("h2") if article else None
        subtitle_tag = article.find("p", class_="subtitle") if article else None
        description_tags = article.find_all("p") if article else []
        description = ""
        for p in description_tags:
            if not p.get("class") or "subtitle" not in p.get("class", []):
                description = p.get_text(strip=True)
                break

        title = h2.get_text(strip=True) if h2 else ""
        subtitle = subtitle_tag.get_text(strip=True) if subtitle_tag else ""

        image_url = ""
        if a_tag and a_tag.get("href"):
            slug = os.path.basename(a_tag["href"].strip("/"))
            image_url = f"https://davinci.edu.ar/uploads/images/noticias/{slug}"

        news_list.append({
            "title": title,
            "subtitle": subtitle,
            "description": description,
            "image": image_url
        })

    return news_list

def parse_sample_contest(html):
    h1 = html.find("h1")
    title = h1.get_text(strip=True) if h1 else ""
    if not re.search(r"Muestra y Concurso", title, re.I):
        return None

    soup = html
    html_str = str(soup)

    converter = MantenerEmbedsConverter()
    md_text = converter.convert(html_str).strip()

    return [
    {
        "template": "sample_contest",
        "title": title,
        "html": html_str,
        "text": md_text,
        "has_sample_contest": True
    }
]


def parse_infraestructura(html):
    h1 = html.find("h1")
    h2 = html.find("h2")
    title_text = (h1.get_text(strip=True) if h1 else "") or (h2.get_text(strip=True) if h2 else "")

    if re.search(r"Infraestructura tecnológica", title_text, re.I):
        ul = html.find("ul")
        items = []

        if ul:
            for li in ul.find_all("li"):
                txt = li.get_text(" ", strip=True)
                if txt:
                    items.append(txt)

        clean_html = "<ul>\n" + "\n".join(f"<li>{i}</li>" for i in items) + "\n</ul>"
        md_text = "\n".join(f"* {i}" for i in items)

        return [
    {
        "template": "infrastructure",
        "title": title_text,
        "html": clean_html,
        "text": md_text,
        "has_infrastructure": True
    }
]

def parse_horarios(html):
    soup = BeautifulSoup(str(html), "lxml")
    items = soup.select("ul.grid.schedules li.item article.box")

    data = []

    for it in items:
        modality = it.find("p", class_="mode")
        modality = modality.get_text(strip=True).upper() if modality else ""

        start = it.find("p", class_="top")
        start_date = start.find("span").get_text(strip=True) if start else ""

        days_el = it.select_one("div.info p.days")
        selected_days = [d.get_text(strip=True) for d in days_el.find_all("span", class_="selected")] if days_el else []
        days = "-".join(selected_days)

        horario_p = None
        for p in it.select("div.info p"):
            if "Día y Hora" in p.get_text():
                horario_p = p
                break
        schedule = horario_p.get_text(strip=True).replace("Día y Hora:", "").strip() if horario_p else ""

        dur_p = None
        for p in it.select("div.info p"):
            if "Duración" in p.get_text():
                dur_p = p
                break
        dur_text = dur_p.get_text(" ", strip=True) if dur_p else ""
        m = re.search(r"(\d+)\s+clases.*?(\d+)\s+horas", dur_text)
        classes = int(m.group(1)) if m else None
        hours = int(m.group(2)) if m else None

        status_p = it.find("p", class_="status")
        open_registration = "open" in status_p.get("class", []) if status_p else False

        data.append({
            "modality": modality,
            "start_date": start_date,
            "days": days,
            "schedule": schedule,
            "classes": classes,
            "hours": hours,
            "open_registration": open_registration
        })

    return data

def parse_certificate(html):
    data_list = []

    software_icon = "https://davinci.edu.ar/uploads/images/icons/software.svg"
    certificate_icon = "https://davinci.edu.ar/uploads/images/icons/certificate.svg"

    ul = html.find("ul", class_="grid")
    if not ul:
        return {"type": "certificate", "data": []}

    for li in ul.find_all("li", class_="certification-box"):
        title_tag = li.find("h2")
        title = title_tag.get_text(strip=True) if title_tag else ""

        lower = title.lower()
        if "software" in lower:
            icon = software_icon
        else:
            icon = certificate_icon

        data_list.append({
            "icon": icon,
            "title": title
        })

    return data_list

def parse_work(html):
    companies = []

    ul = html.find("ul", class_="companies")
    if not ul:
        return {"type": "company", "data": []}

    for li in ul.find_all("li", class_="logo"):
        data_href = li.get("data-href")
        if not data_href:
            continue

        real_url = fix_url(data_href)

        filename = os.path.basename(real_url)
        name_no_ext = os.path.splitext(filename)[0]

        name_clean = re.sub(r"^logo[_-]?", "", name_no_ext, flags=re.I)

        images = [real_url]        
        replacements = write_img(images, real_url, "companies")

        logo_final_url = list(replacements.values())[0] if replacements else ""

        companies.append({
            "name": name_clean,
            "logo": logo_final_url
        })

    return companies

def parse_related_courses(html):
    data = []

    for li in html.select("ul.grid li.item"):
        a_tag = li.find("a", class_="related-box")
        if not a_tag:
            continue

        href = a_tag.get("href", "").strip()
        if not href:
            continue

        url_slug = os.path.basename(href.rstrip("/"))

        h2 = a_tag.find("h2")
        title = h2.get_text(strip=True) if h2 else ""

        p_tag = a_tag.find("p")
        duracion = ""
        if p_tag:
            match = re.search(r"Duración:\s*([\d\w\s]+)", p_tag.get_text())
            if match:
                duracion = match.group(1).strip()

        icon = ""
        color = ""

        json_folder = "titles_json/cursos"
        if os.path.exists(json_folder):
            for fname in os.listdir(json_folder):
                if fname.endswith(".json"):
                    path_json = os.path.join(json_folder, fname)
                    try:
                        with open(path_json, "r", encoding="utf-8") as f:
                            json_data = json.load(f)
                            for section in json_data:  
                                for curso in section.get("items", []):  
                                    curso_url = curso.get("url", "")
                                    curso_slug = os.path.basename(curso_url.rstrip("/"))
                                    if curso_slug == url_slug:
                                        icon = curso.get("icon_path", "") 
                                        color = curso.get("color", "")
                                        break
                                if icon or color:  
                                    break
                    except Exception as e:
                        print(f"Error leyendo {fname}: {e}")

        data.append({
            "title": title,
            "url": url_slug,
            "duracion": duracion,
            "icon": icon,
            "color": color
        })

    return data

def parse_production(html):
    soup = BeautifulSoup(str(html), "lxml")

    text = soup.get_text(" ", strip=True)

    if not any(f in text for f in [
        "Producciones de alumnos",
        "Producciones del Profesor",
        "Trabajos de Alumnos",
        "Trabajos del Profesor"
    ]):
        return parse_content(html)

    data_list = []

    ul = soup.find("ul", class_=lambda c: c and "grid" in c and "small" in c)
    if not ul:
        return {"type": "production", "data": []}

    for idx, li in enumerate(ul.find_all("li", class_="work"), start=1):
        a_tag = li.find("a", class_=lambda c: c and "progressive" in c)
        if not a_tag:
            continue

        name = (
            a_tag.get("data-sub-html") or
            (a_tag.find("img").get("title") if a_tag.find("img") else f"produccion{idx}")
        )

        image_url = a_tag.get("href") or a_tag.get("data-href")
        if not image_url:
            continue

        image_url = fix_url(image_url)

        filename_base = os.path.basename(image_url).split("?")[0]

        replacements = write_img([image_url], filename_base, "production")
        saved_image_url = list(replacements.values())[0] if replacements else image_url

        data_list.append({
            "id_person": "1",
            "name": name,
            "category": "cursos",
            "label": "1",
            "image": saved_image_url
        })

    return {
        "type": "production",
        "data": data_list
    }

def parse_competencies(html):
    soup = BeautifulSoup(str(html), "lxml")

    h1 = soup.find("h1")
    if not h1:
        return None

    title = h1.get_text(strip=True)

    html_items = []
    text_items = []

    ul = soup.find("ul", class_="grid")
    if ul:
        for li in ul.find_all("li", class_="item"):
            box = li.find("article", class_="icon-box")
            if not box:
                continue

            h2 = box.find("h2")
            p = box.find("p")

            title_item = h2.get_text(strip=True) if h2 else ""
            desc_item = p.get_text(strip=True) if p else ""

            html_items.append(f"<li>\n<h2>{title_item}</h2>\n<p>{desc_item}</p>\n</li>")
            text_items.append(f"* **{title_item}**\n\n    {desc_item}")

    aside = soup.find("aside", class_="container")
    if aside:
        h2 = aside.find("h2")
        p = aside.find("p")

        title_item = h2.get_text(strip=True) if h2 else ""
        desc_item = p.get_text(strip=True) if p else ""

        if title_item:
            html_items.append(f"<li>\n<h2>{title_item}</h2>\n<p>{desc_item}</p>\n</li>")
            text_items.append(f"* **{title_item}**\n\n    {desc_item}")

    html_final = "<ul>\n" + "\n".join(html_items) + "\n</ul>"
    text_final = "\n".join(text_items)

    return [
    {
        "template": "featured_list",
        "title": title,
        "html": html_final,
        "text": text_final,
        "has_featured_list": True
    }
]


def write_cursos(curso_data, output_dir="json/cursos"):


    os.makedirs(output_dir, exist_ok=True)

    page = curso_data.get("page")
    if not page:
        raise ValueError("El diccionario no contiene el campo 'page'.")

    file_path = os.path.join(output_dir, f"{page}.json")

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(curso_data, f, ensure_ascii=False, indent=4)

    print(f"Guardado {file_path}")