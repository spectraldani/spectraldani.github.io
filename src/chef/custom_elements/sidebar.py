from chef.custom_elements import icon
from chef.util import make_soup


def render(img_name='avatar'):
    return make_soup(f"""
        <div id="sidebar">
            <link rel="stylesheet" href="/assets/css/sidebar.css">
            <picture>
                <source srcset="/assets/{img_name}.webp" type="image/webp">
                <img alt="" id="avatar" src="/assets/{img_name}.png">
            </picture>
            <h1 class="title"><slot name='title'>
            Daniel Augusto
            </slot></h1>
            
            <nav>
            <ul>
                <li><a href="/">
                    {icon.render('back', 'sidebar')}
                    Return to front page
                </a></li>
                <slot></slot>
            </ul>
            </nav>
        </div>
    """)
