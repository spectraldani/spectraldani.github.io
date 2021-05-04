from bs4 import BeautifulSoup


def render() -> BeautifulSoup:
    return BeautifulSoup(f"""
        <div id="sidebar">
            <link rel="stylesheet" href="/components/sidebar.css">
            <picture>
                <source srcset="/assets/avatar.webp" type="image/webp">
                <img alt="" id="avatar" src="/assets/avatar.png">
            </picture>
            <h1 class="title">Daniel Augusto</h1>
            <a href="/">
            <span class="icon"><svg aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" viewBox="0 0 24 24">
                <use xlink:href="/assets/icons/sidebar.svg#back" width="100"/></svg></span>
            Return to main page
            </a>
        </div>
    """, features='html.parser')
