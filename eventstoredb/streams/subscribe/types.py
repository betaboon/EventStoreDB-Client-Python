from dataclasses import dataclass
from typing import Union
from uuid import UUID

from eventstoredb.streams.types import StreamPosition, StreamRevision


@dataclass
class SubscribeToStreamOptions:
    from_revision: Union[StreamPosition, StreamRevision] = StreamPosition.START
    resolve_links: bool = False


@dataclass
class SubscriptionConfirmation:
    id: UUID
