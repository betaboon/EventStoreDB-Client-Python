from typing import Union, Optional, Iterable

from grpclib.client import Channel

from eventstoredb.generated.event_store.client.streams import StreamsStub


from eventstoredb.client.types import ClientOptions
from eventstoredb.events import EventData
from eventstoredb.streams.append import (
    create_append_header,
    create_append_request,
    convert_append_response,
    AppendResult,
    AppendToStreamOptions,
)


class Client:
    def __init__(self, options: ClientOptions) -> None:
        self.channel = Channel(host=options.host, port=options.port)

    async def append_to_stream(
        self,
        stream_name: str,
        events: Union[EventData, Iterable[EventData]],
        options: Optional[AppendToStreamOptions] = None,
    ) -> AppendResult:

        if isinstance(events, EventData):
            events = [events]

        async def request_iterator():
            yield create_append_header(
                stream_name=stream_name,
                options=options,
            )
            for event in events:
                yield create_append_request(event)

        client = StreamsStub(channel=self.channel)
        response = await client.append(request_iterator())
        return convert_append_response(stream_name, response)
