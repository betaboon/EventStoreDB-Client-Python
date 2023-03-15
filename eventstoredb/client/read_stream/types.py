from __future__ import annotations

from dataclasses import dataclass

from eventstoredb.types import ReadDirection, StreamPosition, StreamRevision


@dataclass
class ReadStreamOptions:
    from_revision: StreamRevision | StreamPosition = StreamPosition.START
    max_count: int = 2**64 - 1  # max-uint64
    direction: ReadDirection = ReadDirection.FORWARDS
    resolve_links: bool = False
