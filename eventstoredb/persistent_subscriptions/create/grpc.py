from typing import Optional

from eventstoredb.generated.event_store.client.persistent_subscriptions import (
    CreateReqOptions,
)

from eventstoredb.persistent_subscriptions.common.grpc import (
    create_create_update_request_options,
)
from eventstoredb.persistent_subscriptions.create.types import (
    CreatePersistentSubscriptionOptions,
)


def create_create_request_options(
    stream_name: str,
    group_name: str,
    options: Optional[CreatePersistentSubscriptionOptions],
) -> CreateReqOptions:
    if options is None:
        options = CreatePersistentSubscriptionOptions()

    request_options = create_create_update_request_options(
        stream_name=stream_name,
        group_name=group_name,
        options=options,
        request_options=CreateReqOptions(),
    )

    return request_options
