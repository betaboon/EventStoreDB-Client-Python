from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from grpclib.client import Channel


class ClientProtocol(Protocol):
    @property
    def channel(self) -> Channel: ...
