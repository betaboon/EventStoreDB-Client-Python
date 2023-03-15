from __future__ import annotations

from eventstoredb.client.delete_persistent_subscription_to_stream.types import (
    DeletePersistentSubscriptionToStreamOptions,
)
from eventstoredb.generated.event_store.client import StreamIdentifier
from eventstoredb.generated.event_store.client.persistent_subscriptions import (
    DeleteReq,
    DeleteReqOptions,
)


def create_delete_persistent_subscription_to_stream_request(
    stream_name: str,
    group_name: str,
    options: DeletePersistentSubscriptionToStreamOptions,
) -> DeleteReq:
    request_options = DeleteReqOptions()

    request_options.stream_identifier = StreamIdentifier(stream_name.encode())
    request_options.group_name = group_name

    return DeleteReq(options=request_options)
