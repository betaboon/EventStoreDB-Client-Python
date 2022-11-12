from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Literal
from uuid import UUID, uuid4


@dataclass
class Position:
    commit: int
    prepare: int


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
    revision: int
    created: int
    position: Position
    data: bytes | None
    metadata: bytes | None


@dataclass
class JsonRecordedEvent(RecordedEvent):
    ...


@dataclass
class BinaryRecordedEvent(RecordedEvent):
    ...


# TODO does this belong to streams/read/types?
@dataclass
class ReadEvent:
    event: RecordedEvent | None = None
    link: RecordedEvent | None = None
    commit_position: int | None = None
