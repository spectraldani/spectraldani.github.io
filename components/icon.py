import components.util as util


def render(type, library, href=None, title=None, label=None):
    soup = util.make_soup(f"""
    <span class="icon">
        <svg aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" viewBox="0 0 24 24">
            <use xlink:href="/assets/icons/{library}.svg#{type}" width="100"/>
        </svg>
    </span>
    """)

    if href is not None:
        soup.span.name = 'a'
        soup.a['href'] = href
        if title is not None:
            soup.a['title'] = title
        if label is not None:
            soup.a['aria-label'] = label

    return soup
