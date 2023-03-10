from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto

StreamRevision = int


class StreamPosition(Enum):
    START = auto()
    END = auto()


@dataclass
class AllPosition:
    commit: int
    prepare: int


@dataclass
class ExcludeSystemEventsFilter:
    ...


@dataclass
class EventTypeFilter:
    regex: str | None = None
    prefix: list[str] | None = None


@dataclass
class StreamNameFilter:
    regex: str | None = None
    prefix: list[str] | None = None
