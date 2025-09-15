import tomllib

import bs4

import chef.util as util
from chef.custom_elements import icon
from chef.bibtex import parse_biblatex, BibtexEntry

biblatex_entries = parse_biblatex(util.get_asset('/pubs/entries.bib'))
database = tomllib.loads(util.get_asset('/entries.toml').read_text(encoding='utf-8'))

for k, v in list(database['authors'].items()):
    for alias in v.get('aliases', []):
        database['authors'][alias] = v


def render_bibentry(entry: BibtexEntry):
    database_entry = database['papers'].get(entry.key, {})
    soup = util.make_soup("""<li class="article">
          <div class="paper-type"></div>
          <div class="paper-preview"></div>
          <div class="paper-info">
            <a class="article-title"></a>.<br>
            <span class="authors"></span>.<br>
            <span class="description"></span>
          </div>
          <div class="icons"></div>
        </li>""")

    soup.li.attrs['id'] = entry.key

    preview_holder = soup.find('div', class_='paper-preview')
    preview_tag = get_preview_tag(entry, soup)
    preview_holder.append(preview_tag)

    # Paper type
    type_holder = soup.find('div', class_='paper-type')
    database_type = database_entry.get('type')

    if database_type == 'workshop' or (
            entry.type == 'InProceedings' and 'workshop' in entry['booktitle'].lower()
    ):
        type_holder.string = 'Workshop'
        css_class = 'workshop'
    elif entry.type == 'InProceedings':
        type_holder.string = 'Conference'
        css_class = entry.type.lower()
    else:
        type_holder.string = entry.type
        css_class = entry.type.lower()
    type_holder['class'].append(css_class)

    # Title
    title_tag: bs4.Tag = soup.find('a', class_='article-title')
    title_tag.string = entry['title']
    if util.get_asset(f'/pubs/{entry.key}.html').exists():
        title_tag.attrs['href'] = f'/pubs/{entry.key}.html'

    # Authors
    authors_span: bs4.Tag = soup.find('span', class_='authors')
    for author in entry.authors[:-1]:
        if database['authors'].get(str(author)) == database['authors']['me']:
            authors_span.append(util.make_soup(f'<b>{author.western()}</b>, '))
        else:
            authors_span.append(f'{author.western()}, ')
    if len(entry.authors) > 1:
        authors_span.append(' and ')
    author = entry.authors[-1]
    if database['authors'].get(str(author)) == database['authors']['me']:
        authors_span.append(util.make_soup(f'<b>{author.western()}</b>'))
    else:
        authors_span.append(f'{author.western()}')

    # Icons
    icons_tag = soup.find('div', class_='icons')
    if util.get_asset(f'/pubs/{entry.key}.md').exists():
        icons_tag.append(util.make_soup(f'<a class="more" href="/pubs/{entry.key}.html">Blogpost</a>'))
    if 'url' in entry.values or 'doi' in entry.values:
        if 'url' in entry.values:
            external_url = entry['url']
        else:
            external_url = 'https://doi.org/' + entry['doi']
        if external_url.endswith('.pdf'):
            icons_tag.append(icon.render(
                'download', 'publication', href=external_url, title='Download paper', label='Download'
            ))
        else:
            icons_tag.append(icon.render(
                'external', 'publication', href=external_url, title='External location',
                label='Go to external location'
            ))
    if 'eprint' in entry.values:
        link = 'https://arxiv.org/abs/' + entry['eprint']
        icons_tag.append(icon.render(
            'arxiv', 'publication', href=link, title='arXiv', label="Go to paper's arXiv page"
        ))
    if 'github' in database_entry:
        link = database_entry['github']
        icons_tag.append(icon.render(
            'github', 'publication', href=link, title='Code', label="Go to paper's GitHub page"
        ))

    # Description
    description_span: bs4.Tag = soup.find('span', class_='description')

    if entry.type == 'InProceedings':
        description_span.string = 'In: {0}'.format(entry['booktitle'])
    elif entry.type == 'Unpublished':
        description_span.string = ''
    elif entry.type == 'Thesis':
        description_span.string = ''
        if entry['type'] == 'mathesis':
            description_span.string += 'M.Sc. thesis. '
        elif entry['type'] == 'phdthesis':
            description_span.string += 'Ph.D. thesis. '
        else:
            raise NotImplementedError(f'Unknown thesis type: {entry["type"]}')

        supervisors = entry.supervisor
        if len(supervisors) == 1:
            supervisor = supervisors[0]
            description_span.string += f'Supervised by {supervisor.western()}'
        else:
            description_span.string += 'Jointly supervised by: '
            description_span.string += ', '.join(supervisor.western() for supervisor in supervisors)
        description_span.string += '. '

        description_span.string += entry['institution']
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
    entries = sorted(biblatex_entries, key=lambda x: x.date)
    entries, draft_entries = util.partition(lambda x: x.type == 'Unpublished', entries)
    # paper_entries, thesis_entries = util.partition(lambda x: x.type == 'Thesis', entries)
    paper_entries = entries

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

    # thesis_list = util.make_soup("""<ul id="publication-list"><h3 class="title">Thesis</h3></ul>""")
    # for entry in thesis_entries:
    #     thesis_list.ul.append(render_bibentry(entry))
    # body.append(thesis_list)

    return body
