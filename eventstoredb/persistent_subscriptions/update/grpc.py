from __future__ import annotations

from eventstoredb.generated.event_store.client.persistent_subscriptions import (
    UpdateReq,
    UpdateReqOptions,
)
from eventstoredb.persistent_subscriptions.common.grpc import (
    create_create_update_request_options,
)
from eventstoredb.persistent_subscriptions.update.types import (
    UpdatePersistentSubscriptionOptions,
)


def create_update_request(
    stream_name: str,
    group_name: str,
    options: UpdatePersistentSubscriptionOptions | None = None,
) -> UpdateReq:
    if options is None:
        options = UpdatePersistentSubscriptionOptions()

    request_options = create_create_update_request_options(
        stream_name=stream_name,
        group_name=group_name,
        options=options,
        request_options=UpdateReqOptions(),
    )

    return UpdateReq(options=request_options)
