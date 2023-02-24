from pathlib import Path

import components.util as util
from components import icon
from components.bibliography import publications, get_preview_tag
from components.bibtex import BibtexEntry

template_html: str = Path('./templates/paper.html').read_text()


def render():
    return {
        f'{pub.key}.html': render_entry(pub)
        for pub in publications
        if pub.type == 'InProceedings' and pub.key.startswith('Souza')
    }


def render_entry(entry: BibtexEntry):
    soup = util.make_soup('<div class="paper-preview"></div>')
    preview_holder = soup.div
    preview_tag = get_preview_tag(entry, soup)
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
        links.append(f"<a href='{external_url}'>{icon.render('external', 'publication')} Paper webpage</a>")
    if 'eprint' in entry.values:
        links.append(
            f"<a href='{'https://arxiv.org/abs/' + entry['eprint'].unescape()}'>{icon.render('arxiv', 'publication')}"
            "Arxiv</a>"
        )
    if 'github_url' in entry.values:
        links.append(f"<a href='{entry['github_url']}'>{icon.render('github', 'publication')} Github</a>")

    if entry.extra_urls is not None:
        for name, link in entry.extra_urls.items():
            links.append(f"<a href='{link}'>{icon.render('external', 'publication')} {name}</a>")

    return template_html.format(
        key=entry.key,
        title=entry['title'],
        authors=authors,
        description='',
        thumbnail_tag=str(preview_holder),
        links=' '.join(links),
        extra_content='',
        extra_sidebar='',
        extra_lang='',
    )
