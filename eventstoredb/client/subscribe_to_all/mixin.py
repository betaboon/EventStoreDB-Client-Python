from __future__ import annotations

from eventstoredb.client.protocol import ClientProtocol
from eventstoredb.client.subscribe_to_all.grpc import (
    convert_subscribe_to_all_response,
    create_subscribe_to_all_request,
)
from eventstoredb.client.subscribe_to_all.types import Checkpoint, SubscribeToAllOptions
from eventstoredb.client.subscribe_to_stream.mixin import Subscription
from eventstoredb.client.subscribe_to_stream.types import SubscriptionConfirmation
from eventstoredb.generated.event_store.client.streams import StreamsStub


class SubscribeToAllMixin(ClientProtocol):
    async def subscribe_to_all(
        self,
        options: SubscribeToAllOptions | None = None,
    ) -> Subscription:
        if options is None:
            options = SubscribeToAllOptions()

        client = StreamsStub(channel=self.channel)
        request = create_subscribe_to_all_request(options=options)

        async for response in client.read(read_req=request):
            response_content = convert_subscribe_to_all_response(response)
            if not isinstance(response_content, Checkpoint) and not isinstance(
                response_content, SubscriptionConfirmation
            ):
                yield response_content
