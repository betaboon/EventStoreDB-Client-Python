from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto


@dataclass
class SubscribeToPersistentSubscriptionToStreamOptions:
    buffer_size: int = 10


@dataclass
class PersistentSubscriptionConfirmation:
    id: str


class NackAction(Enum):
    UNKNOWN = auto()
    PARK = auto()
    RETRY = auto()
    SKIP = auto()
    STOP = auto()
