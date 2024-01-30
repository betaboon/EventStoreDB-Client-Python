from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from eventstoredb.types import AllPosition, ReadDirection, StreamPosition

if TYPE_CHECKING:
    from eventstoredb.filters import (
        EventTypeFilter,
        ExcludeSystemEventsFilter,
        StreamNameFilter,
    )


@dataclass
class ReadAllOptions:
    from_position: AllPosition | StreamPosition = StreamPosition.START
    max_count: int = 2**64 - 1  # max-uint64
    direction: ReadDirection = ReadDirection.FORWARDS
    resolve_links: bool = False
    filter: ExcludeSystemEventsFilter | EventTypeFilter | StreamNameFilter | None = None
