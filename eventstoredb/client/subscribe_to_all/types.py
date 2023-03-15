from __future__ import annotations

from dataclasses import dataclass

from eventstoredb.filters import (
    EventTypeFilter,
    ExcludeSystemEventsFilter,
    StreamNameFilter,
)
from eventstoredb.types import AllPosition, StreamPosition


@dataclass
class SubscribeToAllOptions:
    from_position: AllPosition | StreamPosition = StreamPosition.START
    resolve_links: bool = False
    filter: ExcludeSystemEventsFilter | EventTypeFilter | StreamNameFilter | None = None
    max_search_window: int | None = None
    checkpoint_interval: int = 1


@dataclass
class Checkpoint(AllPosition):
    ...
