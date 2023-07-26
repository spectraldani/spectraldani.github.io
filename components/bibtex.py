import datetime
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Tuple, Optional

entry_re = re.compile(r'^\s*@(\w+)\{(.+),')
value_re = re.compile(r'^\s*(\w+)\s*=\s*(.+),')
and_re = re.compile(r'\band\b')


@dataclass
class BibtexValue:
    key: str
    value: str

    def unescape(self):
        return self.value.replace('{', '').replace('}', '')

    def __str__(self):
        return self.unescape()

    def __repr__(self):
        return f'[{self.key}:{self.value}]'


def parse_author_name(author) -> Tuple[str, str]:
    split_at_comma = author.split(',')
    assert 1 <= len(split_at_comma) <= 2
    if len(split_at_comma) == 2:
        return split_at_comma[0].strip(), split_at_comma[1].strip()
    else:
        split_at_space = author.split(' ')
        return split_at_space[-1], ' '.join(split_at_space[:-1])


date_re = re.compile(r'(\d+)(?:-(\d+)(?:-(\d+))?)?')


@dataclass
class BibtexEntry:
    type: str
    key: str
    values: Dict[str, BibtexValue]

    def __getitem__(self, key):
        return self.values[key]

    @property
    def authors(self) -> List[Tuple[str, str]]:
        """"Returns the 'author' entry properly parsed as (last name, rest)"""
        assert 'author' in self.values
        return [parse_author_name(x.strip()) for x in and_re.split(self['author'].unescape())]

    @property
    def supervisor(self) -> List[Tuple[str, str]]:
        """"Returns the 'supervisor' entry properly parsed as (last name, rest)"""
        assert 'supervisor' in self.values
        return [parse_author_name(x.strip()) for x in and_re.split(self['supervisor'].unescape())]

    @property
    def date(self) -> datetime.date:
        plain_date = self['date'].unescape()
        return datetime.date(*[int(x) if x is not None else 1 for x in date_re.match(plain_date).groups()])

    @property
    def extra_urls(self) -> Optional[Dict[str, str]]:
        urls = self.values.get('extra_urls')
        if urls is not None:
            # noinspection PyTypeChecker
            return dict(
                entries.split(':', 1)
                for entries in urls.unescape().split(',')
            )
        else:
            return None


def parse_biblatex(path: Path) -> List[BibtexEntry]:
    output = []
    with path.open('r', encoding='utf-8') as f:
        current_entry = None
        for line in f:
            if line[0] == '%' or line.startswith('@Comment') or line.strip() == '':
                continue

            entry_matches = entry_re.match(line)
            value_matches = value_re.match(line)
            if entry_matches:
                current_entry = BibtexEntry(*entry_matches.groups(), values={})
            elif value_matches:
                value = BibtexValue(*value_matches.groups())
                current_entry.values[value.key] = value
            elif line[0] == '}':
                output.append(current_entry)
                current_entry = None
            else:
                print(line, end='')
    return output
