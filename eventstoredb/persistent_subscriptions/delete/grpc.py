from typing import Optional

from eventstoredb.generated.event_store.client import StreamIdentifier
from eventstoredb.generated.event_store.client.persistent_subscriptions import (
    DeleteReqOptions,
)

from eventstoredb.persistent_subscriptions.delete.types import (
    DeletePersistentSubscriptionOptions,
)


def create_delete_request_options(
    stream_name: str,
    group_name: str,
    options: Optional[DeletePersistentSubscriptionOptions] = None,
):
    if options is None:
        options = DeletePersistentSubscriptionOptions()

    request_options = DeleteReqOptions()
    request_options.stream_identifier = StreamIdentifier(stream_name.encode())
    request_options.group_name = group_name

    return request_options
