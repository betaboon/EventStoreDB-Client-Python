from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, Union

from eventstoredb.events import Position
from eventstoredb.streams.types import StreamRevision


class AppendExpectedRevision(Enum):
    NO_STREAM = auto()
    ANY = auto()
    STREAM_EXISTS = auto()


@dataclass
class AppendToStreamOptions:
    expected_revision: Union[
        AppendExpectedRevision, StreamRevision
    ] = AppendExpectedRevision.ANY


@dataclass
class AppendResult:
    success: bool
    next_expected_revision: int
    position: Optional[Position] = None
