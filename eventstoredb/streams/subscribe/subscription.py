from typing import AsyncIterator, Optional
from uuid import UUID

from eventstoredb.events import ReadEvent
from eventstoredb.generated.event_store.client.streams import ReadResp
from eventstoredb.streams.subscribe.grpc import convert_read_response
from eventstoredb.streams.subscribe.types import SubscriptionConfirmation


class Subscription(AsyncIterator[ReadEvent]):
    def __init__(self, it: AsyncIterator[ReadResp]) -> None:
        self._it = it
        self.id: Optional[UUID]

    def __aiter__(self) -> AsyncIterator[ReadEvent]:
        return self

    async def __anext__(self) -> ReadEvent:
        while True:
            response = await self._it.__anext__()
            event = convert_read_response(response)
            if isinstance(event, SubscriptionConfirmation):
                self.id = event.id
            else:
                return event
