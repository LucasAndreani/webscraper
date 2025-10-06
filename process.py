from fetch import get_html
from bs4 import BeautifulSoup
from config import URL
from fetch import get_html
from markdownify import markdownify as md


def to_markdown(html):
    soup = BeautifulSoup(html, 'lxml')
    content = soup.find('section', class_='container module-content')
    return md(str(content))

print(to_markdown(get_html(URL)))