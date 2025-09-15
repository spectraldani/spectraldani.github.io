import chef.util as util


def render(src, caption, numbered=False, id=None):
    parsed_caption = util.parse_markdown(caption).p
    parsed_caption.name = 'figcaption'
    soup = util.make_soup(f"""
    <figure {f'id=figure-{id}' if id is not None else ''} {f'class="numbered"' if numbered else ''}>
        <img src={src}>
    </figure>
    """)
    soup.figure.append(parsed_caption)
    return soup
