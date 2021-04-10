from itertools import filterfalse, tee
from pathlib import Path

raw_path = Path('./raw')
cooked_path = Path('./cooked')


def get_asset(path):
    if (raw_path / path).exists():
        return raw_path / path
    else:
        return cooked_path / path


def partition(pred, iterable):
    """Use a predicate to partition entries into false entries and true entries"""
    t1, t2 = tee(iterable)
    return filterfalse(pred, t1), filter(pred, t2)
