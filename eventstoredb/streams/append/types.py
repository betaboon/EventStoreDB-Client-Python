from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto

from eventstoredb.events import Position
from eventstoredb.streams.types import StreamRevision


class AppendExpectedRevision(Enum):
    NO_STREAM = auto()
    ANY = auto()
    STREAM_EXISTS = auto()


@dataclass
class AppendToStreamOptions:
    expected_revision: AppendExpectedRevision | StreamRevision = (
        AppendExpectedRevision.ANY
    )


@dataclass
class AppendResult:
    success: bool
    next_expected_revision: int
    position: Position | None = None
