from __future__ import annotations

from eventstoredb.client.create_persistent_subscription_to_all.types import (
    CreatePersistentSubscriptionToAllOptions,
)
from eventstoredb.client.create_persistent_subscription_to_stream.grpc import (
    create_persistent_subscription_request_settings,
)
from eventstoredb.filters import (
    EventTypeFilter,
    ExcludeSystemEventsFilter,
    StreamNameFilter,
)
from eventstoredb.generated.event_store.client import Empty
from eventstoredb.generated.event_store.client.persistent_subscriptions import (
    CreateReq,
    CreateReqAllOptions,
    CreateReqAllOptionsFilterOptions,
    CreateReqAllOptionsFilterOptionsExpression,
    CreateReqConsumerStrategy,
    CreateReqOptions,
    CreateReqPosition,
    CreateReqSettings,
)
from eventstoredb.types import AllPosition, StreamPosition


def create_create_persistent_subscription_to_all_request(
    group_name: str,
    options: CreatePersistentSubscriptionToAllOptions,
) -> CreateReq:
    request_options = CreateReqOptions()
    request_options.group_name = group_name

    request_options.settings = create_persistent_subscription_request_settings(
        settings=options.settings,
        settings_class=CreateReqSettings,
        consumer_strategy_class=CreateReqConsumerStrategy,
    )

    request_options.all = CreateReqAllOptions()

    if isinstance(options.from_position, AllPosition):
        request_options.all.position = CreateReqPosition()
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

    if not options.filter:
        request_options.all.no_filter = Empty()
    else:
        request_options.all.filter = CreateReqAllOptionsFilterOptions()
        filter_expression = CreateReqAllOptionsFilterOptionsExpression()

        if isinstance(options.filter, ExcludeSystemEventsFilter):
            filter_expression.regex = "^[^\\$].*"
        else:
            if options.filter.regex:
                filter_expression.regex = options.filter.regex
            if options.filter.prefix:
                filter_expression.prefix = options.filter.prefix

        if isinstance(options.filter, ExcludeSystemEventsFilter):
            request_options.all.filter.event_type = filter_expression
        elif isinstance(options.filter, EventTypeFilter):
            request_options.all.filter.event_type = filter_expression
        elif isinstance(options.filter, StreamNameFilter):
            request_options.all.filter.stream_identifier = filter_expression

        if options.max_search_window is not None:
            request_options.all.filter.max = options.max_search_window
        else:
            request_options.all.filter.count = Empty()

        request_options.all.filter.checkpoint_interval_multiplier = (
            options.checkpoint_interval
        )

    return CreateReq(options=request_options)
