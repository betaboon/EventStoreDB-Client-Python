from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from eventstoredb.types import AllPosition, StreamRevision


class AppendExpectedRevision(Enum):
    NO_STREAM = auto()
    ANY = auto()
    STREAM_EXISTS = auto()


@dataclass
class AppendToStreamOptions:
    expected_revision: AppendExpectedRevision | StreamRevision = AppendExpectedRevision.ANY


@dataclass
class AppendResult:
    success: bool
    next_expected_revision: StreamRevision
    position: AllPosition | None = None
