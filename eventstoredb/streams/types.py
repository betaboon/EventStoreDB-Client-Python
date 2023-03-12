from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from uuid import UUID

from eventstoredb.types import Position

StreamRevision = int


class StreamPosition(Enum):
    START = auto()
    END = auto()


@dataclass
class Checkpoint(Position):
    ...


@dataclass
class ExcludeSystemEventsFilter:
    ...


@dataclass
class EventTypeFilter:
    regex: str | None = None
    prefix: list[str] | None = None


@dataclass
class StreamNameFilter:
    regex: str | None = None
    prefix: list[str] | None = None


@dataclass
class SubscriptionConfirmation:
    id: UUID
