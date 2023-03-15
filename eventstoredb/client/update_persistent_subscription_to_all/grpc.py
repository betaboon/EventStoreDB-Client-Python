from __future__ import annotations

from eventstoredb.client.create_persistent_subscription_to_all.grpc import (
    create_persistent_subscription_request_settings,
)
from eventstoredb.client.update_persistent_subscription_to_all.types import (
    UpdatePersistentSubscriptionToAllOptions,
)
from eventstoredb.generated.event_store.client import Empty
from eventstoredb.generated.event_store.client.persistent_subscriptions import (
    UpdateReq,
    UpdateReqAllOptions,
    UpdateReqConsumerStrategy,
    UpdateReqOptions,
    UpdateReqPosition,
    UpdateReqSettings,
)
from eventstoredb.types import AllPosition, StreamPosition


def create_update_persistent_subscription_to_all_request(
    group_name: str,
    options: UpdatePersistentSubscriptionToAllOptions,
) -> UpdateReq:
    request_options = UpdateReqOptions()
    request_options.all = UpdateReqAllOptions()
    request_options.group_name = group_name

    if isinstance(options.from_position, AllPosition):
        request_options.all.position = UpdateReqPosition()
        request_options.all.position.commit_position = (
            options.from_position.commit_position
        )
        request_options.all.position.prepare_position = (
            options.from_position.prepare_position
        )
    elif options.from_position == StreamPosition.START:
        request_options.all.start = Empty()
    elif options.from_position == StreamPosition.END:
        request_options.all.end = Empty()

    request_options.settings = create_persistent_subscription_request_settings(
        settings=options.settings,
        settings_class=UpdateReqSettings,
        consumer_strategy_class=UpdateReqConsumerStrategy,
    )

    return UpdateReq(options=request_options)
