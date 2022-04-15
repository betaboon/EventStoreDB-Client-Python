import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Literal, Optional
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
    # NOTE order matters here because we override attributes with default-values in subclasses
    type: str
    content_type: ContentType
    id: UUID = field(default_factory=uuid4)
    data: Optional[bytes] = None
    metadata: Optional[bytes] = None

    def _serialized_data(self) -> Optional[bytes]:
        return self.data

    def _serialized_metadata(self) -> Optional[bytes]:
        return self.metadata


@dataclass
class JsonEvent(EventData):
    content_type: Literal[ContentType.JSON] = ContentType.JSON
    # TODO it would be great not to use Any here
    data: Optional[Any] = None
    # TODO it would be great not to use Any here
    metadata: Optional[Any] = None

    def _serialized_data(self) -> Optional[bytes]:
        if self.data:
            json_data = json.dumps(self.data)
            return json_data.encode()

    def _serialized_metadata(self) -> Optional[bytes]:
        if self.metadata:
            json_data = json.dumps(self.metadata)
            return json_data.encode()


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
    data: Optional[Any]
    # TODO it would be great not to use Any here
    metadata: Optional[Any]


@dataclass
class BinaryRecordedEvent(RecordedEvent):
    data: Optional[bytes]
    metadata: Optional[bytes]


# TODO does this belong to streams/read/types?
@dataclass
class ReadEvent:
    event: Optional[RecordedEvent] = None
    link: Optional[RecordedEvent] = None
    commit_position: Optional[int] = None
