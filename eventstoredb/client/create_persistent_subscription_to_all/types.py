from __future__ import annotations

from dataclasses import dataclass, field

from eventstoredb.client.create_persistent_subscription_to_stream.types import (
    PersistentSubscriptionSettings,
)
from eventstoredb.filters import (
    EventTypeFilter,
    ExcludeSystemEventsFilter,
    StreamNameFilter,
)
from eventstoredb.types import AllPosition, StreamPosition


@dataclass
class CreatePersistentSubscriptionToAllOptions:
    settings: PersistentSubscriptionSettings = field(
        default_factory=PersistentSubscriptionSettings
    )
    from_position: AllPosition | StreamPosition = StreamPosition.START
    filter: ExcludeSystemEventsFilter | EventTypeFilter | StreamNameFilter | None = None
    max_search_window: int | None = None
    checkpoint_interval: int = 1
