import importlib.util
import itertools
import re
from importlib import import_module
from pathlib import Path
from typing import Dict

import bs4.element
from bs4 import BeautifulSoup

import components.util

raw_folder = Path('./raw')
cooked_folder = Path('./cooked')

tag_regex = re.compile(r'dani:(.+)')


def main():
    for path_to_process in raw_folder.rglob('*.export.py'):
        cook_py(path_to_process)
    for path_to_process in raw_folder.rglob('*.export.html'):
        cook_html(path_to_process)


def cook_py(path):
    spec = importlib.util.spec_from_file_location('', path)
    script = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(script)

    root_path = cooked_folder / path.relative_to(raw_folder).parent
    render_result: Dict[str, str] = script.render() or {}
    for filename, content in render_result.items():
        if filename.endswith('.html'):
            content = str(cook_html_string(content))
        (root_path / filename).parent.mkdir(parents=True, exist_ok=True)
        (root_path / filename).write_text(content, encoding='utf-8')


def cook_html(path):
    soup = cook_html_string(path.read_text(encoding='utf-8'))
    processed_path = path.relative_to(raw_folder).with_name(path.name.replace('.export', ''))
    cooked_path = (cooked_folder / processed_path)
    cooked_path.write_text(str(soup), encoding='utf-8')


def cook_html_string(html_string: str) -> BeautifulSoup:
    soup = components.util.make_soup(html_string)

    # Call special dani tags
    for tags_to_process in soup.find_all(tag_regex):
        module_name = tag_regex.match(tags_to_process.name)[1].replace('-', '_')
        module = import_module('components.' + module_name)

        rendered_tag: BeautifulSoup = module.render(**tags_to_process.attrs)

        children_by_slot = {
            slot_name: list(elements)
            for slot_name, elements in itertools.groupby(
                sorted(tags_to_process.children, key=lambda x: getattr(x, 'attrs', {}).get('slot', '')),
                key=lambda x: getattr(x, 'attrs', {}).get('slot', None)
            )
        }
        for slot in rendered_tag.find_all('slot'):
            slot_name = slot.attrs.get('name', None)
            if slot_name in children_by_slot:
                slot.contents = children_by_slot[slot_name]
            slot.unwrap()

        tags_to_process.replace_with(rendered_tag)

    # Remove comments
    for comment_tags in soup.find_all(string=lambda x: isinstance(x, bs4.element.Comment)):
        comment_tags.extract()

    return soup


if __name__ == '__main__':
    main()
