from __future__ import annotations

from grpclib.exceptions import GRPCError

from eventstoredb.client.create_persistent_subscription_to_all.grpc import (
    create_create_persistent_subscription_to_all_request,
)
from eventstoredb.client.create_persistent_subscription_to_all.types import (
    CreatePersistentSubscriptionToAllOptions,
)
from eventstoredb.client.create_persistent_subscription_to_stream.grpc import (
    convert_grpc_error_to_exception,
)
from eventstoredb.client.protocol import ClientProtocol
from eventstoredb.generated.event_store.client.persistent_subscriptions import (
    PersistentSubscriptionsStub,
)


class CreatePersistentSubscriptionToAllMixin(ClientProtocol):
    async def create_persistent_subscription_to_all(
        self,
        group_name: str,
        options: CreatePersistentSubscriptionToAllOptions | None = None,
    ) -> None:
        if options is None:
            options = CreatePersistentSubscriptionToAllOptions()

        client = PersistentSubscriptionsStub(channel=self.channel)
        request = create_create_persistent_subscription_to_all_request(
            group_name=group_name,
            options=options,
        )

        try:
            await client.create(create_req=request)
        except GRPCError as e:
            raise convert_grpc_error_to_exception(e)
