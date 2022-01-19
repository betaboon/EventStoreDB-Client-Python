from dataclasses import dataclass
from enum import Enum, auto
from typing import Union

from eventstoredb.streams.types import (
    StreamPosition,
    StreamRevision,
)


class ReadDirection(Enum):
    FORWARDS = auto()
    BACKWARDS = auto()


@dataclass
class ReadStreamOptions:
    from_revision: Union[StreamPosition, StreamRevision] = StreamPosition.START
    max_count: int = 2 ** 64 - 1  # max-uint64
    direction: ReadDirection = ReadDirection.FORWARDS
    resolve_links: bool = False
