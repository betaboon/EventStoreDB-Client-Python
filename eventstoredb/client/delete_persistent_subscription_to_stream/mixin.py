from __future__ import annotations

from grpclib.exceptions import GRPCError

from eventstoredb.client.create_persistent_subscription_to_stream.grpc import (
    convert_grpc_error_to_exception,
)
from eventstoredb.client.delete_persistent_subscription_to_stream.grpc import (
    create_delete_persistent_subscription_to_stream_request,
)
from eventstoredb.client.delete_persistent_subscription_to_stream.types import (
    DeletePersistentSubscriptionToStreamOptions,
)
from eventstoredb.client.protocol import ClientProtocol
from eventstoredb.generated.event_store.client.persistent_subscriptions import (
    PersistentSubscriptionsStub,
)


class DeletePersistentSubscriptionToStreamMixin(ClientProtocol):
    async def delete_persistent_subscription_to_stream(
        self,
        stream_name: str,
        group_name: str,
        options: DeletePersistentSubscriptionToStreamOptions | None = None,
    ) -> None:
        if options is None:
            options = DeletePersistentSubscriptionToStreamOptions()

        client = PersistentSubscriptionsStub(channel=self.channel)
        request = create_delete_persistent_subscription_to_stream_request(
            stream_name=stream_name,
            group_name=group_name,
            options=options,
        )

        try:
            await client.delete(delete_req=request)
        except GRPCError as e:
            raise convert_grpc_error_to_exception(e)
