from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from eventstoredb.streams.types import (
    EventTypeFilter,
    ExcludeSystemEventsFilter,
    StreamNameFilter,
    StreamPosition,
    StreamRevision,
)
from eventstoredb.types import Position


@dataclass
class SubscribeToStreamOptions:
    from_revision: StreamPosition | StreamRevision = StreamPosition.START
    resolve_links: bool = False


@dataclass
class SubscribeToAllOptions:
    from_position: StreamPosition | Position = StreamPosition.START
    resolve_links: bool = False
    filter: ExcludeSystemEventsFilter | EventTypeFilter | StreamNameFilter | None = None
    max_search_window: int | None = None
    checkpoint_interval: int = 1


@dataclass
class SubscriptionConfirmation:
    id: UUID
