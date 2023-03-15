from __future__ import annotations

from eventstoredb.client.protocol import ClientProtocol
from eventstoredb.client.subscribe_to_persistent_subscription_to_all.grpc import (
    create_read_request,
)
from eventstoredb.client.subscribe_to_persistent_subscription_to_all.types import (
    SubscribeToPersistentSubscriptionToAllOptions,
)
from eventstoredb.client.subscribe_to_persistent_subscription_to_stream.mixin import (
    PersistentSubscription,
)


class SubscribeToPersistentSubscriptionToAllMixin(ClientProtocol):
    def subscribe_to_persistent_subscription_to_all(
        self,
        group_name: str,
        options: SubscribeToPersistentSubscriptionToAllOptions | None = None,
    ) -> PersistentSubscription:
        if options is None:
            options = SubscribeToPersistentSubscriptionToAllOptions()

        request = create_read_request(
            group_name=group_name,
            options=options,
        )

        return PersistentSubscription(
            channel=self.channel,
            read_request=request,
        )
