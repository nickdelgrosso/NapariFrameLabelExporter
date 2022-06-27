from typing import NamedTuple


class Progress(NamedTuple):
    value: int
    max: int
    description: str = ''
