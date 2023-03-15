from __future__ import annotations

from typing import AsyncIterator

from eventstoredb.client.protocol import ClientProtocol
from eventstoredb.client.read_all.grpc import create_read_all_request
from eventstoredb.client.read_all.types import ReadAllOptions
from eventstoredb.client.read_stream.grpc import convert_read_response
from eventstoredb.events import ReadEvent
from eventstoredb.generated.event_store.client.streams import StreamsStub


class ReadAllMixin(ClientProtocol):
    async def read_all(
        self,
        options: ReadAllOptions | None = None,
    ) -> AsyncIterator[ReadEvent]:
        if options is None:
            options = ReadAllOptions()

        client = StreamsStub(channel=self.channel)
        request = create_read_all_request(options=options)

        # TODO raise exception StreamNotFoundError
        async for response in client.read(read_req=request):
            response_content = convert_read_response(response)
            if isinstance(response_content, ReadEvent):
                yield response_content
