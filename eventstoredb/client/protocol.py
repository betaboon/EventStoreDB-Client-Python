from __future__ import annotations

from typing import Protocol

from grpclib.client import Channel


class ClientProtocol(Protocol):
    @property
    def channel(self) -> Channel:
        ...
