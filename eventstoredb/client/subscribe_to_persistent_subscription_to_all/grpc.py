from __future__ import annotations

from eventstoredb.client.subscribe_to_persistent_subscription_to_all.types import (
    SubscribeToPersistentSubscriptionToAllOptions,
)
from eventstoredb.generated.event_store.client import Empty
from eventstoredb.generated.event_store.client.persistent_subscriptions import (
    ReadReq,
    ReadReqOptions,
    ReadReqOptionsUuidOption,
)


def create_read_request(
    group_name: str,
    options: SubscribeToPersistentSubscriptionToAllOptions,
) -> ReadReq:
    request_options = ReadReqOptions()
    request_options.all = Empty()
    request_options.group_name = group_name
    request_options.buffer_size = options.buffer_size
    request_options.uuid_option = ReadReqOptionsUuidOption(string=Empty())
    return ReadReq(options=request_options)
