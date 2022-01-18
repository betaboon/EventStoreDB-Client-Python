from typing import Union, Optional, Iterable, AsyncIterator

from grpclib.client import Channel
from grpclib.exceptions import GRPCError

from eventstoredb.generated.event_store.client.streams import StreamsStub
from eventstoredb.generated.event_store.client.persistent_subscriptions import (
    PersistentSubscriptionsStub,
)


from eventstoredb.client.types import ClientOptions
from eventstoredb.events import (
    EventData,
    ReadEvent,
)
from eventstoredb.streams.append import (
    create_append_header,
    create_append_request,
    convert_append_response,
    AppendResult,
    AppendToStreamOptions,
)
from eventstoredb.streams.read import (
    create_read_request_options,
    convert_read_response,
    ReadStreamOptions,
)
from eventstoredb.streams.subscribe import (
    create_stream_subscription_options,
    Subscription,
    SubscribeToStreamOptions,
)
from eventstoredb.persistent_subscriptions.common import (
    convert_grpc_error_to_exception,
)
from eventstoredb.persistent_subscriptions.create import (
    create_create_request_options,
    CreatePersistentSubscriptionOptions,
)
from eventstoredb.persistent_subscriptions.update import (
    create_update_request_options,
    UpdatePersistentSubscriptionOptions,
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

    async def read_stream(
        self,
        stream_name: str,
        options: Optional[ReadStreamOptions] = None,
    ) -> AsyncIterator[ReadEvent]:
        client = StreamsStub(channel=self.channel)
        request_options = create_read_request_options(
            stream_name=stream_name,
            options=options,
        )
        # TODO raise exception StreamNotFoundError
        async for response in client.read(options=request_options):
            yield convert_read_response(response)

    def subscribe_to_stream(
        self, stream_name: str, options: Optional[SubscribeToStreamOptions] = None
    ) -> Subscription:
        client = StreamsStub(channel=self.channel)
        request_options = create_stream_subscription_options(
            stream_name=stream_name,
            options=options,
        )
        it = client.read(options=request_options)
        return Subscription(it)

    async def create_persistent_subscription(
        self,
        stream_name: str,
        group_name: str,
        options: Optional[CreatePersistentSubscriptionOptions] = None,
    ) -> None:
        client = PersistentSubscriptionsStub(channel=self.channel)
        request_options = create_create_request_options(
            stream_name=stream_name,
            group_name=group_name,
            options=options,
        )
        try:
            await client.create(options=request_options)
        except GRPCError as e:
            raise convert_grpc_error_to_exception(e)

    async def update_persistent_subscription(
        self,
        stream_name: str,
        group_name: str,
        options: Optional[UpdatePersistentSubscriptionOptions] = None,
    ) -> None:
        client = PersistentSubscriptionsStub(channel=self.channel)
        request_options = create_update_request_options(
            stream_name=stream_name,
            group_name=group_name,
            options=options,
        )
        try:
            await client.update(options=request_options)
        except GRPCError as e:
            raise convert_grpc_error_to_exception(e)
