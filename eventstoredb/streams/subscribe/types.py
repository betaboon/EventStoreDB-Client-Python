from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from eventstoredb.streams.types import StreamPosition, StreamRevision


@dataclass
class SubscribeToStreamOptions:
    from_revision: StreamPosition | StreamRevision = StreamPosition.START
    resolve_links: bool = False


@dataclass
class SubscriptionConfirmation:
    id: UUID
