from __future__ import annotations

from typing import AsyncIterator
from uuid import UUID

import betterproto

from eventstoredb.events import ReadEvent
from eventstoredb.generated.event_store.client.streams import ReadResp
from eventstoredb.streams.read.grpc import convert_read_response_read_event
from eventstoredb.streams.subscribe.grpc import convert_read_response_confirmation


class Subscription(AsyncIterator[ReadEvent]):
    def __init__(self, it: AsyncIterator[ReadResp]) -> None:
        self._it = it
        self.id: UUID | None

    def __aiter__(self) -> AsyncIterator[ReadEvent]:
        return self

    async def __anext__(self) -> ReadEvent:
        while True:
            response = await self._it.__anext__()

            content_type, _ = betterproto.which_one_of(response, "content")
            if content_type == "confirmation":
                event = convert_read_response_confirmation(response.confirmation)
                self.id = event.id
            elif content_type == "event":
                return convert_read_response_read_event(response.event)
