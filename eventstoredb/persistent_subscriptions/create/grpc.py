from __future__ import annotations

from eventstoredb.generated.event_store.client.persistent_subscriptions import (
    CreateReq,
    CreateReqOptions,
)
from eventstoredb.persistent_subscriptions.common.grpc import (
    create_create_update_request_options,
)
from eventstoredb.persistent_subscriptions.create.types import (
    CreatePersistentSubscriptionOptions,
)


def create_create_request(
    stream_name: str,
    group_name: str,
    options: CreatePersistentSubscriptionOptions | None = None,
) -> CreateReq:
    if options is None:
        options = CreatePersistentSubscriptionOptions()

    request_options = create_create_update_request_options(
        stream_name=stream_name,
        group_name=group_name,
        options=options,
        request_options=CreateReqOptions(),
    )

    return CreateReq(options=request_options)
