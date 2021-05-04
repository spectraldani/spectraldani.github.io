import bs4
from bs4 import BeautifulSoup

import components.misc as misc
from components.bibtex import parse_biblatex, BibtexEntry

publications = parse_biblatex(misc.get_asset('pubs/entries.bib'))


# <a class="icon" title="Arxiv" aria-label="Go to paper's archive page"
# href="https://arxiv.org/abs/1907.01867">
# <svg aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="1em" height="1em"
# viewBox="0 0 24 24">
# <use xlink:href="icons.svg#arxiv"></use>
# </svg>
# </a>
# <a class="icon" title="Code" aria-label="Go to paper's GitHub page"
# href="https://github.com/spectraldani/UnscentedGPLVM">
# <svg aria-hidden="true" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 480 512">
# <use xlink:href="icons.svg#github"></use>
# </svg>
# </a>

def render_icon(link, id, title, label=None):
    return BeautifulSoup(f"""
    <a class="icon" title="{title}" {'aria-label="{0}"'.format(label) if label else ''} href="{link}">
    <svg aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" viewBox="0 0 24 24">
        <use xlink:href="/assets/icons/publication.svg#{id}" width="100"/>
    </svg>
    </a>""", 'html.parser')


def render_bibentry(entry: BibtexEntry) -> BeautifulSoup:
    soup = BeautifulSoup("""<li class="article">
          <div class="paper-preview"></div>
          <div>
            <span class="authors"></span>.
            <a class="article-title"></a>.
            <span class="description"></span>
          </div>
          <div class="icons"></div>
        </li>""", 'html.parser')

    soup.li.attrs['id'] = entry.key

    preview_holder = soup.find('div', class_='paper-preview')
    preview_img_path = '/pubs/thumbs/{0}.svg'.format(entry.key)
    preview_img = misc.get_asset('.' + preview_img_path)
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

    # Title
    title_tag: bs4.Tag = soup.find('a', class_='article-title')
    title_tag.string = entry['title'].unescape()
    if misc.get_asset(f'pubs/{entry.key}.html').exists():
        title_tag.attrs['href'] = f'./pubs/{entry.key}.html'

    # Authors
    authors_span: bs4.Tag = soup.find('span', class_='authors')
    author_list = [' '.join(x[::-1]) for x in entry.authors]
    if len(author_list) > 1:
        authors_span.string = '{0}, and {1}'.format(', '.join(author_list[:-1]), author_list[-1])
    else:
        authors_span.string = author_list[0]

    # Icons
    icons_tag = soup.find('div', class_='icons')
    if 'url' in entry.values or 'doi' in entry.values:
        if 'url' in entry.values:
            external_url = entry['url'].unescape()
        else:
            external_url = 'https://doi.org/' + entry['doi'].unescape()
        icons_tag.append(render_icon(
            external_url,
            'external',
            'External location',
            'Go to paper\'s external location',
        ))
    if 'eprint' in entry.values:
        icons_tag.append(render_icon(
            'https://arxiv.org/abs/' + entry['eprint'].unescape(),
            'arxiv',
            'arXiv',
            'Go to paper\'s arXiv page'
        ))
    if 'github_url' in entry.values:
        icons_tag.append(render_icon(
            entry['github_url'].unescape(),
            'github',
            'Code',
            'Go to paper\'s GitHub page'
        ))

    # Description
    description_span: bs4.Tag = soup.find('span', class_='description')

    if entry.type == 'InProceedings':
        description_span.string = 'In: {0}'.format(entry['booktitle'].unescape())
    elif entry.type == 'Thesis':
        description_span.string = ''
        if entry['type'].unescape() == 'mathesis':
            description_span.string += 'M.Sc. thesis. '
        elif entry['type'].unescape() == 'phdthesis':
            description_span.string += 'Ph.D. thesis. '
        else:
            raise NotImplementedError(f'Unknown thesis type: {entry["type"]}')

        supervisors = entry.supervisor
        if len(supervisors) == 1:
            supervisor = supervisors[0]
            description_span.string += f'Supervised by {supervisor[1]} {supervisor[0]}'
        else:
            description_span.string += 'Jointly supervised by: '
            description_span.string += ', '.join(' '.join(supervisor[::-1]) for supervisor in supervisors)
        description_span.string += '. '

        description_span.string += entry['institution'].unescape()
    else:
        raise Exception('Unknown entry type: {0}'.format(entry.type))
    return soup


def render() -> BeautifulSoup:
    body = BeautifulSoup("""<div id="bibliography"></div>""", 'html.parser')
    entries = sorted(publications, key=lambda x: x.date)
    paper_entries, thesis_entries = misc.partition(lambda x: x.type == 'Thesis', entries)

    publication_list = BeautifulSoup("""<h2 class="title">Bibliography</h2><ul id="publication-list"></ul>""",
                                     'html.parser')
    current_year = -1
    current_item = None
    for entry in paper_entries:
        if entry.date.year > current_year:
            current_year = entry.date.year
            if current_item is not None:
                publication_list.ul.insert(0, current_item)
            current_item = publication_list.new_tag('li')
            current_item.append(publication_list.new_tag('h3'))
            current_item.h3.string = str(current_year)
            current_item.h3.attrs['class'] = 'title'
            current_item.append(publication_list.new_tag('ul'))
        current_item.ul.append(render_bibentry(entry))
    publication_list.ul.insert(0, current_item)
    body.append(publication_list)

    thesis_list = BeautifulSoup("""<ul id="publication-list"><h3 class="title">Thesis</h3></ul>""", 'html.parser')
    for entry in thesis_entries:
        thesis_list.ul.append(render_bibentry(entry))
    body.append(thesis_list)

    return body
