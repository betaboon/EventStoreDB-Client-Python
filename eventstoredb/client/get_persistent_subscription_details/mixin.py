from __future__ import annotations

from grpclib.exceptions import GRPCError

from eventstoredb.client.create_persistent_subscription_to_stream.grpc import (
    convert_grpc_error_to_exception,
)
from eventstoredb.client.get_persistent_subscription_details.grpc import (
    convert_get_persistent_subscription_details_response,
    create_get_persistent_subscription_details_request,
)
from eventstoredb.client.get_persistent_subscription_details.types import (
    GetPersistentSubscriptionDetailsOptions,
    SubscriptionDetails,
)
from eventstoredb.client.protocol import ClientProtocol
from eventstoredb.generated.event_store.client.persistent_subscriptions import (
    PersistentSubscriptionsStub,
)


class GetPersistentSubscriptionDetailsMixin(ClientProtocol):
    async def get_persistent_subscription_details(
        self,
        stream_name: str,
        group_name: str,
        options: GetPersistentSubscriptionDetailsOptions | None = None,
    ) -> SubscriptionDetails:
        if options is None:
            options = GetPersistentSubscriptionDetailsOptions()

        client = PersistentSubscriptionsStub(channel=self.channel)
        request = create_get_persistent_subscription_details_request(
            stream_name=stream_name,
            group_name=group_name,
            options=options,
        )

        try:
            response = await client.get_info(get_info_req=request)
        except GRPCError as e:
            raise convert_grpc_error_to_exception(e)  # noqa: B904,TRY200

        return convert_get_persistent_subscription_details_response(response)
