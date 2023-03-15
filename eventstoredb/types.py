from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto

Position = int
StreamRevision = int


class StreamPosition(Enum):
    START = auto()
    END = auto()


class ReadDirection(Enum):
    FORWARDS = auto()
    BACKWARDS = auto()


@dataclass
class AllPosition:
    commit_position: int
    prepare_position: int
