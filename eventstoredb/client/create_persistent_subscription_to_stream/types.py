from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto

from eventstoredb.types import StreamPosition, StreamRevision


class ConsumerStrategy(Enum):
    DISPATCH_TO_SINGLE = auto()
    ROUND_ROBIN = auto()
    PINNED = auto()


@dataclass
class PersistentSubscriptionSettings:
    resolve_links: bool = False
    extra_statistics: bool = False
    message_timeout: int = 30000
    max_retry_count: int = 10
    checkpoint_after: int = 2000
    min_checkpoint_count: int = 10
    max_checkpoint_count: int = 1000
    max_subscriber_count: int = 0
    live_buffer_size: int = 500
    read_batch_size: int = 20
    history_buffer_size: int = 500
    consumer_strategy: ConsumerStrategy = ConsumerStrategy.ROUND_ROBIN


@dataclass
class CreatePersistentSubscriptionToStreamOptions:
    settings: PersistentSubscriptionSettings = field(
        default_factory=PersistentSubscriptionSettings
    )
    from_revision: StreamRevision | StreamPosition = StreamPosition.START
