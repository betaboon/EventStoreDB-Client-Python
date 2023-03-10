from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto

from eventstoredb.streams.types import (
    AllPosition,
    EventTypeFilter,
    ExcludeSystemEventsFilter,
    StreamNameFilter,
    StreamPosition,
    StreamRevision,
)


class ReadDirection(Enum):
    FORWARDS = auto()
    BACKWARDS = auto()


@dataclass
class ReadStreamOptions:
    from_revision: StreamPosition | StreamRevision = StreamPosition.START
    max_count: int = 2**64 - 1  # max-uint64
    direction: ReadDirection = ReadDirection.FORWARDS
    resolve_links: bool = False


@dataclass
class ReadAllOptions:
    from_position: StreamPosition | AllPosition = StreamPosition.START
    max_count: int = 2**64 - 1  # max-uint64
    direction: ReadDirection = ReadDirection.FORWARDS
    resolve_links: bool = False
    filter: ExcludeSystemEventsFilter | EventTypeFilter | StreamNameFilter | None = None
