from pathlib import Path

from bs4 import BeautifulSoup

import components.misc as misc
from components.bibliography import publications
from components.bibtex import BibtexEntry

template_html: str = misc.get_asset('pubs/templates/paper.html').read_text()


def render():
    return {
        f'{pub.key}.html': render_entry(pub)
        for pub in publications
        if pub.type == 'InProceedings' and pub.key.startswith('Souza')
    }


def svg_icon(id):
    return f'''<svg aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" viewBox="0 0 24 24">
        <use xlink:href="/assets/icons/publication.svg#{id}" width="100"/>
    </svg>'''.strip()


def render_entry(entry: BibtexEntry):
    soup = BeautifulSoup('<div class="paper-preview"></div>', 'html.parser')
    preview_holder = soup.div
    preview_img_path = './thumbs/{0.key}.svg'.format(entry)
    preview_img = misc.get_asset('pubs' / Path(preview_img_path))
    if preview_img.exists():
        preview_tag = soup.new_tag('img', alt='', src=preview_img_path)
        preview_tag.attrs['width'] = '5'
        preview_tag.attrs['height'] = '7.071'
    else:
        preview_tag = soup.new_tag('div', attrs={"class": "text"})
        if entry.type == 'Unpublished':
            preview_tag.string = 'DRAFT'
        else:
            preview_tag.string = 'NO\u00A0IMG'
    preview_holder.append(preview_tag)

    author_list = [' '.join(x[::-1]).replace(' ', '\u00A0') for x in entry.authors]
    if len(author_list) > 1:
        authors = '{0}, and {1}'.format(', '.join(author_list[:-1]), author_list[-1])
    else:
        authors = author_list[0]

    links = []
    if 'url' in entry.values or 'doi' in entry.values:
        if 'url' in entry.values:
            external_url = entry['url'].unescape()
        else:
            external_url = 'https://doi.org/' + entry['doi'].unescape()
        links.append(f'''
        <a href='{external_url}'>{svg_icon('external')} Paper webpage</a>
        '''.strip())
    if 'eprint' in entry.values:
        links.append(f'''
        <a href='{'https://arxiv.org/abs/' + entry['eprint'].unescape()}'>{svg_icon('arxiv')} Arxiv</a>
        '''.strip())
    if 'github_url' in entry.values:
        links.append(f'''
        <a href='{entry['github_url']}'>{svg_icon('github')} Github</a>
        '''.strip())

    return template_html.format(
        key=entry.key,
        title=entry['title'],
        authors=authors,
        description='',
        thumbnail_tag=str(preview_holder),
        links=' '.join(links),
        extra_content='',
    )
