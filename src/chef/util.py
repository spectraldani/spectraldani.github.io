import collections
import re
import subprocess
from itertools import filterfalse, tee
from pathlib import Path

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


def parse_markdown(md: str) -> BeautifulSoup:
    process = subprocess.run(
        ['pandoc', '-f', 'markdown', '-t', 'html', '--gladtex'],
        capture_output=True, input=md.encode('utf-8'), text=False
    )
    if process.returncode == 0:
        return make_soup(process.stdout.decode('utf-8'))
    else:
        raise Exception(f'pandoc failed: {process.stdout}\n{process.stderr}')


class FrozenDict[TK, TV](dict[TK, TV]):
    def __setitem__(self, key, value):
        raise TypeError("This dictionary is read-only")

    def __delitem__(self, key):
        raise TypeError("This dictionary is read-only")

    def clear(self):
        raise TypeError("This dictionary is read-only")

    def pop(self, key, default=None):
        raise TypeError("This dictionary is read-only")

    def popitem(self):
        raise TypeError("This dictionary is read-only")

    def setdefault(self, key, default=None):
        raise TypeError("This dictionary is read-only")

    def update(self, *args, **kwargs):
        raise TypeError("This dictionary is read-only")

    def __hash__(self):
        return hash(frozenset(self.items()))
