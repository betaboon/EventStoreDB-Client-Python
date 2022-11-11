from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Literal
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
    # NOTE order matters due to dataclass-inheritence
    type: str
    content_type: ContentType
    id: UUID = field(default_factory=uuid4)
    data: bytes | None = None
    metadata: bytes | None = None

    def _serialized_data(self) -> bytes | None:
        return self.data

    def _serialized_metadata(self) -> bytes | None:
        return self.metadata


@dataclass
class JsonEvent(EventData):
    content_type: Literal[ContentType.JSON] = ContentType.JSON
    # TODO it would be great not to use Any here
    data: Any | None = None
    # TODO it would be great not to use Any here
    metadata: Any | None = None

    def _serialized_data(self) -> bytes | None:
        if self.data:
            json_data = json.dumps(self.data)
            return json_data.encode()
        return None

    def _serialized_metadata(self) -> bytes | None:
        if self.metadata:
            json_data = json.dumps(self.metadata)
            return json_data.encode()
        return None


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


@dataclass
class JsonRecordedEvent(RecordedEvent):
    # TODO it would be great not to use Any here
    data: Any | None
    # TODO it would be great not to use Any here
    metadata: Any | None


@dataclass
class BinaryRecordedEvent(RecordedEvent):
    data: bytes | None
    metadata: bytes | None


# TODO does this belong to streams/read/types?
@dataclass
class ReadEvent:
    event: RecordedEvent | None = None
    link: RecordedEvent | None = None
    commit_position: int | None = None
