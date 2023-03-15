from __future__ import annotations

from typing import AsyncIterator

from eventstoredb.client.protocol import ClientProtocol
from eventstoredb.client.read_stream.grpc import (
    convert_read_response,
    create_read_request,
)
from eventstoredb.client.read_stream.types import ReadStreamOptions
from eventstoredb.events import ReadEvent
from eventstoredb.generated.event_store.client.streams import StreamsStub


class ReadStreamMixin(ClientProtocol):
    async def read_stream(
        self,
        stream_name: str,
        options: ReadStreamOptions | None = None,
    ) -> AsyncIterator[ReadEvent]:
        if options is None:
            options = ReadStreamOptions()

        client = StreamsStub(channel=self.channel)
        request = create_read_request(
            stream_name=stream_name,
            options=options,
        )

        # TODO raise exception StreamNotFoundError
        async for response in client.read(read_req=request):
            response_content = convert_read_response(response)
            if isinstance(response_content, ReadEvent):
                yield response_content
