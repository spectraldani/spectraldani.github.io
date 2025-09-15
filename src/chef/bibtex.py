import datetime
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from chef.util import FrozenDict

__all__ = ['Author', 'BibtexEntry', 'parse_biblatex']

log = logging.getLogger(__name__)

entry_re = re.compile(r'^\s*@(\w+)\{(.+),')
value_re = re.compile(r'^\s*(\w+)\s*=\s*(.+),')
and_re = re.compile(r'\band\b')
date_re = re.compile(r'(\d+)(?:-(\d+)(?:-(\d+))?)?')


@dataclass(frozen=True)
class Author:
    last_name: str
    rest: str

    def __str__(self):
        return f'{self.last_name}, {self.rest}'

    def western(self, nbsp: bool = False) -> str:
        """Returns the author name in Western format (first name last name)"""
        s = f'{self.rest} {self.last_name}'
        if not nbsp:
            return s
        else:
            return s.replace(' ', '\u00A0')

    @staticmethod
    def from_str(author: str) -> 'Author':
        split_at_comma = author.split(',')
        assert 1 <= len(split_at_comma) <= 2
        if len(split_at_comma) == 2:
            return Author(split_at_comma[0].strip(), split_at_comma[1].strip())
        else:
            split_at_space = author.split(' ')
            return Author(split_at_space[-1], ' '.join(split_at_space[:-1]))


@dataclass(frozen=True)
class BibtexEntry:
    type: str
    key: str
    values: FrozenDict[str, str]

    def __getitem__(self, key):
        return self.values[key]

    @property
    def authors(self) -> List[Author]:
        """Returns the 'author' entry properly parsed as (last name, rest)"""
        assert 'author' in self.values
        return [Author.from_str(x.strip()) for x in and_re.split(self['author'])]

    @property
    def supervisor(self) -> List[Author]:
        """Returns the 'supervisor' entry properly parsed as (last name, rest)"""
        assert 'supervisor' in self.values
        return [Author.from_str(x.strip()) for x in and_re.split(self['supervisor'])]

    @property
    def date(self) -> datetime.date:
        return datetime.date(*[int(x) if x is not None else 1 for x in date_re.match(self['date']).groups()])
ø

def unescape_latex(latex: str) -> str:
    return latex.replace('{', '').replace('}', '').replace(r'\&', '&')


def parse_biblatex(path: Path) -> List[BibtexEntry]:
    output = []
    with path.open('r', encoding='utf-8') as f:
        current_entry = None
        for line in f:
            if line[0] == '%' or line.startswith('@Comment') or line.strip() == '':
                continue

            if entry_matches := entry_re.match(line):
                type, key = entry_matches.groups()
                current_entry = [type, key, {}]
            elif value_matches := value_re.match(line):
                key, value = value_matches.groups()
                current_entry[-1][key] = unescape_latex(value)
            elif line[0] == '}':
                type, key, values = current_entry
                output.append(BibtexEntry(type, key, FrozenDict(values)))
                current_entry = None
            else:
                log.warning(f'Unknown line {line!r}')
    return output
