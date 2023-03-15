from __future__ import annotations

from grpclib.exceptions import GRPCError

from eventstoredb.client.create_persistent_subscription_to_stream.grpc import (
    convert_grpc_error_to_exception,
)
from eventstoredb.client.protocol import ClientProtocol
from eventstoredb.client.update_persistent_subscription_to_all.grpc import (
    create_update_persistent_subscription_to_all_request,
)
from eventstoredb.client.update_persistent_subscription_to_all.types import (
    UpdatePersistentSubscriptionToAllOptions,
)
from eventstoredb.generated.event_store.client.persistent_subscriptions import (
    PersistentSubscriptionsStub,
)


class UpdatePersistentSubscriptionToAllMixin(ClientProtocol):
    async def update_persistent_subscription_to_all(
        self,
        group_name: str,
        options: UpdatePersistentSubscriptionToAllOptions | None = None,
    ) -> None:
        if options is None:
            options = UpdatePersistentSubscriptionToAllOptions()

        client = PersistentSubscriptionsStub(channel=self.channel)
        request = create_update_persistent_subscription_to_all_request(
            group_name=group_name,
            options=options,
        )

        try:
            await client.update(update_req=request)
        except GRPCError as e:
            raise convert_grpc_error_to_exception(e)
