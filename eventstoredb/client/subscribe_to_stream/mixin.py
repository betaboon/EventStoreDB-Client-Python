from __future__ import annotations

from typing import AsyncIterator, Union

from eventstoredb.client.protocol import ClientProtocol
from eventstoredb.client.subscribe_to_stream.grpc import (
    convert_subscribe_to_stream_response,
    create_subscribe_to_stream_request,
)
from eventstoredb.client.subscribe_to_stream.types import (
    SubscribeToStreamOptions,
    SubscriptionConfirmation,
)
from eventstoredb.events import CaughtUp, FellBehind, ReadEvent
from eventstoredb.generated.event_store.client.streams import StreamsStub

# NOTE not using union-operator for python3.9 compatibility
# yes, even from __future__ import annotations does not help
Subscription = AsyncIterator[Union[ReadEvent, CaughtUp, FellBehind]]


class SubscribeToStreamMixin(ClientProtocol):
    async def subscribe_to_stream(
        self,
        stream_name: str,
        options: SubscribeToStreamOptions | None = None,
    ) -> Subscription:
        if options is None:
            options = SubscribeToStreamOptions()

        client = StreamsStub(channel=self.channel)
        request = create_subscribe_to_stream_request(
            stream_name=stream_name,
            options=options,
        )

        async for response in client.read(read_req=request):
            response_content = convert_subscribe_to_stream_response(response)
            if not isinstance(response_content, SubscriptionConfirmation):
                yield response_content
