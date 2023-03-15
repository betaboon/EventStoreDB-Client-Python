from __future__ import annotations

from dataclasses import dataclass

from eventstoredb.types import StreamPosition, StreamRevision


@dataclass
class SubscribeToStreamOptions:
    from_revision: StreamRevision | StreamPosition = StreamPosition.START
    resolve_links: bool = False


@dataclass
class SubscriptionConfirmation:
    id: str
