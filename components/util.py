from itertools import filterfalse, tee
from pathlib import Path

import requests
from bs4 import BeautifulSoup

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
