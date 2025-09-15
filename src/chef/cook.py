import importlib.util
import itertools
import re
import sys
import time
from importlib import import_module
from pathlib import Path
from typing import Callable

import bs4.element
from bs4 import BeautifulSoup
from tqdm import tqdm

import chef.util as util
from chef.custom_elements.latex import process_eq_tags

raw_folder = Path('./raw')
cooked_folder = Path('./cooked')

tag_regex = re.compile(r'dani:(.+)')

def main():
    current_location = Path(__file__).parent
    build_log = (cooked_folder / 'build.log')
    if build_log.exists():
        build_log_lines = build_log.read_text(encoding='utf-8').splitlines()
        existing_paths = {Path(path) for path in build_log_lines[1:]}
    else:
        existing_paths = {}

    build_timestamp = int(time.time())
    paths_to_generate = {}

    for path in raw_folder.rglob('*.export.*'):
        root_path = cooked_folder / path.relative_to(raw_folder).parent
        match path.suffix:
            case '.py':
                paths_to_generate.update({
                    (root_path / filename): (
                        lambda render=render: str(cook_html_string(render())) if filename.endswith('.html') else render
                    )
                    for filename, render in build_py(path).items()
                })
            case '.html':
                paths_to_generate[root_path / path.name.replace('.export', '')] = (
                    lambda path=path: str(cook_html_string(path.read_text(encoding='utf-8')))
                )

    paths_to_delete = existing_paths - paths_to_generate.keys()
    for path in paths_to_delete:
        print('Deleting', path, flush=True, file=sys.stderr)
        assert path.resolve().is_relative_to(current_location)
        path.unlink(missing_ok=True)

    for path, render in paths_to_generate.items():
        print('Generating', path, flush=True, file=sys.stderr)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render(), encoding='utf-8')

    build_log.write_text(
        f'{build_timestamp}\n' + '\n'.join(map(str, paths_to_generate)),
        encoding='utf-8'
    )


def build_py(path: Path) -> dict[str, Callable[[], str]]:
    spec = importlib.util.spec_from_file_location('', path)
    script = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(script)
    if not hasattr(script, 'build') or not callable(script.build):
        raise ValueError(f"Module {path} does not have a callable 'build' function.")
    return script.build()


def cook_py(path) -> list[Path]:
    paths_generated = []
    spec = importlib.util.spec_from_file_location('', path)
    script = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(script)

    root_path = cooked_folder / path.relative_to(raw_folder).parent
    render_result: dict[str, str] = script.render() or {}
    for filename, content in render_result.items():
        print('Processing', filename, flush=True, file=sys.stderr)
        if filename.endswith('.html'):
            content = str(cook_html_string(content))
        (root_path / filename).parent.mkdir(parents=True, exist_ok=True)
        (root_path / filename).write_text(content, encoding='utf-8')
        paths_generated.append(root_path / filename)
    return paths_generated


def cook_html_string(html_string: str) -> BeautifulSoup:
    soup = util.make_soup(html_string)

    # Call special dani tags
    for tags_to_process in tqdm(soup.find_all(tag_regex), desc='\tSpecial tags', ):
        module_name = tag_regex.match(tags_to_process.name)[1].replace('-', '_')
        module = import_module('chef.components.' + module_name)

        rendered_tag: BeautifulSoup = module.render(**{
            k.replace('-', '_'): v
            for k, v in tags_to_process.attrs.items()
        })

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

    # Process equation tags
    eqs = soup.find_all('eq')
    if eqs:
        process_eq_tags(eqs)

    # Remove comments
    for comment_tags in soup.find_all(string=lambda x: isinstance(x, bs4.element.Comment)):
        comment_tags.extract()

    return soup


if __name__ == '__main__':
    main()
