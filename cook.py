import re
from importlib import import_module
from pathlib import Path

from bs4 import BeautifulSoup

raw_folder = Path('./raw')
cooked_folder = Path('./cooked')

tag_regex = re.compile(r'dani:(.+)')


def main():
    for path_to_process in raw_folder.rglob('*.export.html'):
        with path_to_process.open('r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), "html.parser")
            for tags_to_process in soup.find_all(tag_regex):
                module_name = tag_regex.match(tags_to_process.name)[1].replace('-', '_')
                module = import_module('components.' + module_name)
                tags_to_process.replace_with(module.render())

        processed_path = path_to_process.relative_to(raw_folder).with_name(path_to_process.name.replace('.export', ''))
        cooked_path = (cooked_folder / processed_path)
        with cooked_path.open('w', encoding='utf-8') as f:
            f.write(str(soup))


def test_bibtex():
    import components.bibliography
    for p in sorted(components.bibliography.publications, key=lambda x: x.date):
        print(components.bibliography.render_bibentry(p))


if __name__ == '__main__':
    main()
