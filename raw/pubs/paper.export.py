from functools import partial
from importlib.resources import files

import chef.util as util
from chef.custom_elements import icon
from chef.custom_elements.bibliography import biblatex_entries, database, get_preview_tag
from chef.custom_elements.bibtex import BibtexEntry

template_html: str = files('chef.templates').joinpath('paper.html').read_text()


def build():
    return {
        f'{pub.key}.html': partial(render_entry, pub, database['papers'].get(pub.key, {}))
        for pub in biblatex_entries
        if pub.type in ['InProceedings', 'Unpublished'] and
           (pub.key.startswith('Souza') or util.get_asset(f'/pubs/{pub.key}.md').exists())
    }


def render_entry(entry: BibtexEntry, database_entry: dict) -> str:
    soup = util.make_soup('<div class="paper-preview"></div>')
    preview_holder = soup.div
    preview_tag = get_preview_tag(entry, soup)
    preview_holder.append(preview_tag)

    author_list = [x.western(nbsp=True) for x in entry.authors]
    if len(author_list) > 1:
        authors = '{0}, and {1}'.format(', '.join(author_list[:-1]), author_list[-1])
    else:
        authors = author_list[0]

    links = []
    if 'url' in entry.values or 'doi' in entry.values:
        icon_type = 'external'
        if 'url' in entry.values:
            external_url = entry['url']
            if 'openreview.net' in external_url:
                icon_type = 'openreview'
        else:
            external_url = 'https://doi.org/' + entry['doi']
        if external_url.endswith('.pdf'):
            links.append(f"<a href='{external_url}'>{icon.render('download', 'publication')} PDF</a>")
        else:
            links.append(f"<a href='{external_url}'>{icon.render(icon_type, 'publication')} URL</a>")
    if 'eprint' in entry.values:
        links.append(
            f"<a href='{'https://arxiv.org/abs/' + entry['eprint']}'>{icon.render('arxiv', 'publication')}"
            "Arxiv</a>"
        )
    if 'github_url' in entry.values:
        links.append(f"<a href='{entry['github_url']}'>{icon.render('github', 'publication')} Github</a>")

    if 'poster' in database_entry:
        links.append(
            f"<a href='{database_entry['poster']}'>{icon.render('download', 'publication')} Poster</a>"
        )

    if 'slides' in database_entry:
        links.append(
            f"<a href='{database_entry['slides']}'>{icon.render('download', 'publication')} Slides</a>"
        )

    for name, link in database_entry.get('extra_urls', {}).items():
        if name == 'OpenReview':
            icon_type = 'openreview'
        else:
            icon_type = 'external'
        links.append(f"<a href='{link}'>{icon.render(icon_type, 'publication')} {name}</a>")

    extra_content_path = util.get_asset(f'/pubs/{entry.key}.md')
    extra_content = (
        util.parse_markdown(extra_content_path.read_text(encoding='utf-8'))
        if extra_content_path.is_file() else
        ''
    )

    return util.format_html_str(
        template_html,
        util.FormatValues(
            key=entry.key,
            title=entry['title'],
            authors=authors,
            thumbnail_tag=str(preview_holder),
            links=' '.join(links),
            extra_content=extra_content,
            extra_lang='en-US'
        )
    )
