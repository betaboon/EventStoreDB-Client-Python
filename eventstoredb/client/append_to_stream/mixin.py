from __future__ import annotations

from typing import AsyncGenerator, Iterable

from eventstoredb.client.append_to_stream.grpc import (
    convert_append_response,
    create_append_header,
    create_append_request,
)
from eventstoredb.client.append_to_stream.types import (
    AppendResult,
    AppendToStreamOptions,
)
from eventstoredb.client.protocol import ClientProtocol
from eventstoredb.events import EventData
from eventstoredb.generated.event_store.client.streams import AppendReq, StreamsStub


class AppendToStreamMixin(ClientProtocol):
    async def append_to_stream(
        self,
        stream_name: str,
        events: EventData | Iterable[EventData],
        options: AppendToStreamOptions | None = None,
    ) -> AppendResult:
        if options is None:
            options = AppendToStreamOptions()

        async def request_iterator() -> AsyncGenerator[AppendReq, None]:
            yield create_append_header(
                stream_name=stream_name,
                options=options,
            )
            if isinstance(events, EventData):
                yield create_append_request(events)
            else:
                for event in events:
                    yield create_append_request(event)

        client = StreamsStub(channel=self.channel)
        response = await client.append(request_iterator())
        return convert_append_response(stream_name, response)
