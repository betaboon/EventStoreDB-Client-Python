from __future__ import annotations

from grpclib.exceptions import GRPCError

from eventstoredb.client.create_persistent_subscription_to_stream.grpc import (
    convert_grpc_error_to_exception,
    create_create_persistent_subscription_to_stream_request,
)
from eventstoredb.client.create_persistent_subscription_to_stream.types import (
    CreatePersistentSubscriptionToStreamOptions,
)
from eventstoredb.client.protocol import ClientProtocol
from eventstoredb.generated.event_store.client.persistent_subscriptions import (
    PersistentSubscriptionsStub,
)


class CreatePersistentSubscriptionToStreamMixin(ClientProtocol):
    async def create_persistent_subscription_to_stream(
        self,
        stream_name: str,
        group_name: str,
        options: CreatePersistentSubscriptionToStreamOptions | None = None,
    ) -> None:
        if options is None:
            options = CreatePersistentSubscriptionToStreamOptions()

        client = PersistentSubscriptionsStub(channel=self.channel)
        request = create_create_persistent_subscription_to_stream_request(
            stream_name=stream_name,
            group_name=group_name,
            options=options,
        )

        try:
            await client.create(create_req=request)
        except GRPCError as e:
            raise convert_grpc_error_to_exception(e)
