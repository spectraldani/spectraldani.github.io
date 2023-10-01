import bs4

import components.util as util
from components import icon
from components.bibtex import parse_biblatex, BibtexEntry

publications = parse_biblatex(util.get_asset('/pubs/entries.bib'))


def render_bibentry(entry: BibtexEntry):
    soup = util.make_soup("""<li class="article">
          <div class="paper-preview"></div>
          <div>
            <span class="authors"></span>.
            <a class="article-title"></a>.
            <span class="description"></span>
          </div>
          <div class="icons"></div>
        </li>""")

    soup.li.attrs['id'] = entry.key

    preview_holder = soup.find('div', class_='paper-preview')
    preview_tag = get_preview_tag(entry, soup)
    preview_holder.append(preview_tag)

    # Title
    title_tag: bs4.Tag = soup.find('a', class_='article-title')
    title_tag.string = entry['title'].unescape()
    if util.get_asset(f'/pubs/{entry.key}.html').exists():
        title_tag.attrs['href'] = f'/pubs/{entry.key}.html'

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
        icons_tag.append(icon.render('external', 'publication', href=external_url, title='External location',
                                     label='Go to paper\'s external location'))
    if 'eprint' in entry.values:
        link = 'https://arxiv.org/abs/' + entry['eprint'].unescape()
        icons_tag.append(
            icon.render('arxiv', 'publication', href=link, title='arXiv', label='Go to paper\'s arXiv page'))
    if 'github_url' in entry.values:
        link = entry['github_url'].unescape()
        icons_tag.append(
            icon.render('github', 'publication', href=link, title='Code', label='Go to paper\'s GitHub page'))

    # Description
    description_span: bs4.Tag = soup.find('span', class_='description')

    if entry.type == 'InProceedings':
        description_span.string = 'In: {0}'.format(entry['booktitle'].unescape())
    elif entry.type == 'Unpublished':
        description_span.string = ''
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


def get_preview_tag(entry: BibtexEntry, soup: bs4.BeautifulSoup) -> bs4.Tag:
    preview_img_path = '/pubs/thumbs/{0}.svg'.format(entry.key)
    preview_img = util.get_asset(preview_img_path)
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
    return preview_tag


def render():
    body = util.make_soup("""<div id="bibliography"><h2 class="title">Bibliography</h2></div>""")
    entries = sorted(publications, key=lambda x: x.date)
    entries, draft_entries = util.partition(lambda x: x.type == 'Unpublished', entries)
    paper_entries, thesis_entries = util.partition(lambda x: x.type == 'Thesis', entries)

    draft_entries = list(draft_entries)
    if len(draft_entries) > 0:
        draft_list = util.make_soup("""<ul id="publication-list"><h3 class="title">Drafts</h3></ul>""")
        for entry in draft_entries:
            draft_list.ul.append(render_bibentry(entry))
        body.append(draft_list)

    publication_list = util.make_soup("""<ul id="publication-list"></ul>""")
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

    thesis_list = util.make_soup("""<ul id="publication-list"><h3 class="title">Thesis</h3></ul>""")
    for entry in thesis_entries:
        thesis_list.ul.append(render_bibentry(entry))
    body.append(thesis_list)

    return body
