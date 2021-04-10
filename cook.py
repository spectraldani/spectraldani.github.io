import importlib.util
import re
from importlib import import_module
from pathlib import Path
from typing import Dict

from bs4 import BeautifulSoup

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
        (root_path / filename).write_text(content, encoding='utf-8')


def cook_html(path):
    soup = BeautifulSoup(path.read_text(encoding='utf-8'), "html.parser")
    for tags_to_process in soup.find_all(tag_regex):
        module_name = tag_regex.match(tags_to_process.name)[1].replace('-', '_')
        module = import_module('components.' + module_name)
        tags_to_process.replace_with(module.render())
    processed_path = path.relative_to(raw_folder).with_name(path.name.replace('.export', ''))
    cooked_path = (cooked_folder / processed_path)
    cooked_path.write_text(str(soup), encoding='utf-8')


if __name__ == '__main__':
    main()
