from components import icon
from components.util import make_soup


def render():
    return make_soup(f"""
        <div id="sidebar">
            <link rel="stylesheet" href="/assets/css/sidebar.css">
            <picture>
                <source srcset="/assets/avatar.webp" type="image/webp">
                <img alt="" id="avatar" src="/assets/avatar.png">
            </picture>
            <h1 class="title">Daniel Augusto</h1>
            
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
