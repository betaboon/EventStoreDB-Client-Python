from dataclasses import dataclass
from typing import Optional
from enum import Enum, auto
from uuid import UUID


from eventstoredb.events import ReadEvent


@dataclass
class SubscribeToPersistentSubscriptionOptions:
    buffer_size: int = 10


@dataclass
class PersistentSubscriptionEvent(ReadEvent):
    retry_count: Optional[int] = None

    @property
    def original_id(self) -> UUID:
        if self.link:
            return self.link.id
        elif self.event:
            return self.event.id
        else:
            # TODO raise better exception
            # NOTE this should never happen
            raise Exception("i should never be here")


@dataclass
class PersistentSubscriptionConfirmation:
    id: str


class NackAction(Enum):
    UNKNOWN = auto()
    PARK = auto()
    RETRY = auto()
    SKIP = auto()
    STOP = auto()
