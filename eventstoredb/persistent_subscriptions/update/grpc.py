from typing import Optional

from eventstoredb.generated.event_store.client.persistent_subscriptions import (
    UpdateReqOptions,
)
from eventstoredb.persistent_subscriptions.common.grpc import (
    create_create_update_request_options,
)
from eventstoredb.persistent_subscriptions.update.types import (
    UpdatePersistentSubscriptionOptions,
)


def create_update_request_options(
    stream_name: str,
    group_name: str,
    options: Optional[UpdatePersistentSubscriptionOptions],
) -> UpdateReqOptions:
    if options is None:
        options = UpdatePersistentSubscriptionOptions()

    request_options = create_create_update_request_options(
        stream_name=stream_name,
        group_name=group_name,
        options=options,
        request_options=UpdateReqOptions(),
    )

    return request_options
