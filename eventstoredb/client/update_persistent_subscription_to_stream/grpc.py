from __future__ import annotations

from eventstoredb.client.create_persistent_subscription_to_stream.grpc import (
    create_persistent_subscription_request_settings,
)
from eventstoredb.client.update_persistent_subscription_to_stream.types import (
    UpdatePersistentSubscriptionToStreamOptions,
)
from eventstoredb.generated.event_store.client import Empty, StreamIdentifier
from eventstoredb.generated.event_store.client.persistent_subscriptions import (
    UpdateReq,
    UpdateReqConsumerStrategy,
    UpdateReqOptions,
    UpdateReqSettings,
    UpdateReqStreamOptions,
)
from eventstoredb.types import StreamPosition, StreamRevision


def create_update_persistent_subscription_to_stream_request(
    stream_name: str,
    group_name: str,
    options: UpdatePersistentSubscriptionToStreamOptions,
) -> UpdateReq:
    request_options = UpdateReqOptions()
    request_options.stream = UpdateReqStreamOptions()
    request_options.stream.stream_identifier = StreamIdentifier(stream_name.encode())
    request_options.group_name = group_name

    if isinstance(options.from_revision, StreamRevision):
        request_options.stream.revision = options.from_revision
    elif options.from_revision == StreamPosition.START:
        request_options.stream.start = Empty()
    elif options.from_revision == StreamPosition.END:
        request_options.stream.end = Empty()

    request_options.settings = create_persistent_subscription_request_settings(
        settings=options.settings,
        settings_class=UpdateReqSettings,
        consumer_strategy_class=UpdateReqConsumerStrategy,
    )

    return UpdateReq(options=request_options)
