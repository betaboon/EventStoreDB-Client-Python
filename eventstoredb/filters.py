from __future__ import annotations

from dataclasses import dataclass


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
