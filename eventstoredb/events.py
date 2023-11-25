from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Literal
from uuid import UUID, uuid4

from eventstoredb.types import AllPosition, Position, StreamRevision


class ContentType(str, Enum):
    BINARY = "application/octet-stream"
    JSON = "application/json"


@dataclass
class EventData:
    type: str
    content_type: ContentType
    id: UUID = field(default_factory=uuid4)
    data: bytes | None = None
    metadata: bytes | None = None


@dataclass
class JsonEvent(EventData):
    content_type: Literal[ContentType.JSON] = ContentType.JSON


@dataclass
class BinaryEvent(EventData):
    content_type: Literal[ContentType.BINARY] = ContentType.BINARY


@dataclass
class RecordedEvent:
    stream_name: str
    id: UUID
    type: str
    content_type: ContentType
    revision: StreamRevision
    created: int
    position: AllPosition
    data: bytes | None
    metadata: bytes | None


@dataclass
class JsonRecordedEvent(RecordedEvent):
    ...


@dataclass
class BinaryRecordedEvent(RecordedEvent):
    ...


@dataclass
class ReadEvent:
    event: RecordedEvent | None = None
    link: RecordedEvent | None = None
    commit_position: Position | None = None


@dataclass
class CaughtUp:
    ...


@dataclass
class FellBehind:
    ...


@dataclass
class PersistentSubscriptionEvent(ReadEvent):
    retry_count: int | None = None
