from __future__ import annotations

from typing import AsyncIterator

from eventstoredb.client.protocol import ClientProtocol
from eventstoredb.client.subscribe_to_stream.grpc import (
    convert_subscribe_to_stream_response,
    create_subscribe_to_stream_request,
)
from eventstoredb.client.subscribe_to_stream.types import SubscribeToStreamOptions
from eventstoredb.events import ReadEvent
from eventstoredb.generated.event_store.client.streams import StreamsStub

Subscription = AsyncIterator[ReadEvent]


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
            if isinstance(response_content, ReadEvent):
                yield response_content
