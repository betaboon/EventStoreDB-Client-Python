from __future__ import annotations

from eventstoredb.client.delete_persistent_subscription_to_all.types import (
    DeletePersistentSubscriptionToAllOptions,
)
from eventstoredb.generated.event_store.client import Empty
from eventstoredb.generated.event_store.client.persistent_subscriptions import (
    DeleteReq,
    DeleteReqOptions,
)


def create_delete_persistent_subscription_to_all_request(
    group_name: str,
    options: DeletePersistentSubscriptionToAllOptions,
) -> DeleteReq:
    request_options = DeleteReqOptions()

    request_options.all = Empty()
    request_options.group_name = group_name

    return DeleteReq(options=request_options)
