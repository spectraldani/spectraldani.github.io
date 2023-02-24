import collections
import re
from itertools import filterfalse, tee
from pathlib import Path

import requests
from bs4 import BeautifulSoup

js_python = re.compile(r"\bpy`(.+?)`")

raw_path = Path('./raw')
cooked_path = Path('./cooked')
download_path = Path('./cache')


def get_asset(path):
    if type(path) is str:
        path = Path(path)
    path = path.relative_to('/')
    if (raw_path / path).exists():
        return raw_path / path
    else:
        return cooked_path / path


class FormatValues(collections.defaultdict):
    def __init__(self, **kwargs):
        super().__init__(lambda: '', **kwargs)


def format_html_str(x: str, format_values: dict) -> str:
    x_soup = make_soup(x)
    for tag in x_soup.find_all('script'):
        if tag.string is not None:
            js_script = str(tag.string)
            js_script = js_python.sub(lambda m: format_values[m.group(1)], js_script)
            js_script = js_script.replace('{', '{{').replace('}', '}}')
            tag.string.replace_with(js_script)
    return str(x_soup).format_map(format_values)


def partition(pred, iterable):
    """Use a predicate to partition entries into false entries and true entries"""
    t1, t2 = tee(iterable)
    return filterfalse(pred, t1), filter(pred, t2)


def make_soup(x: str) -> BeautifulSoup:
    return BeautifulSoup(x, features='html.parser')


def http_get(url, *args, **kwargs):
    cache_file = (download_path / f'{hash(url)}')
    if cache_file.exists():
        return cache_file.read_text(encoding='utf-8')
    else:
        data = requests.get(url, *args, **kwargs).text
        cache_file.write_text(data, encoding='utf-8')
        return data
