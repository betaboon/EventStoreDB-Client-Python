from __future__ import annotations

from uuid import UUID

from eventstoredb.generated.event_store.client import Empty, StreamIdentifier
from eventstoredb.generated.event_store.client.streams import (
    ReadReq,
    ReadReqOptions,
    ReadReqOptionsAllOptions,
    ReadReqOptionsFilterOptions,
    ReadReqOptionsFilterOptionsExpression,
    ReadReqOptionsPosition,
    ReadReqOptionsStreamOptions,
    ReadReqOptionsSubscriptionOptions,
    ReadReqOptionsUuidOption,
    ReadRespSubscriptionConfirmation,
)
from eventstoredb.streams.subscribe.types import (
    SubscribeToAllOptions,
    SubscribeToStreamOptions,
    SubscriptionConfirmation,
)
from eventstoredb.streams.types import (
    AllPosition,
    EventTypeFilter,
    ExcludeSystemEventsFilter,
    StreamNameFilter,
    StreamPosition,
    StreamRevision,
)


def create_read_request_options_common(
    options: SubscribeToAllOptions | SubscribeToStreamOptions,
) -> ReadReqOptions:
    request_options = ReadReqOptions()

    request_options.resolve_links = options.resolve_links
    request_options.uuid_option = ReadReqOptionsUuidOption(string=Empty())
    request_options.subscription = ReadReqOptionsSubscriptionOptions()

    return request_options


def create_subscribe_to_stream_request(
    stream_name: str,
    options: SubscribeToStreamOptions | None = None,
) -> ReadReq:
    if options is None:
        options = SubscribeToStreamOptions()

    request_options = create_read_request_options_common(options)

    request_options.no_filter = Empty()

    request_options.stream = ReadReqOptionsStreamOptions()
    request_options.stream.stream_identifier = StreamIdentifier(stream_name.encode())

    if isinstance(options.from_revision, StreamRevision):
        request_options.stream.revision = options.from_revision
    elif options.from_revision == StreamPosition.START:
        request_options.stream.start = Empty()
    elif options.from_revision == StreamPosition.END:
        request_options.stream.end = Empty()

    return ReadReq(options=request_options)


def create_subscribe_to_all_request(
    options: SubscribeToAllOptions | None = None,
) -> ReadReq:
    if options is None:
        options = SubscribeToAllOptions()

    request_options = create_read_request_options_common(options)

    request_options.all = ReadReqOptionsAllOptions()

    if isinstance(options.from_position, AllPosition):
        request_options.all.position = ReadReqOptionsPosition()
        request_options.all.position.commit_position = options.from_position.commit
        request_options.all.position.prepare_position = options.from_position.prepare
    elif options.from_position == StreamPosition.START:
        request_options.all.start = Empty()
    elif options.from_position == StreamPosition.END:
        request_options.all.end = Empty()

    if not options.filter:
        request_options.no_filter = Empty()
    else:
        request_options.filter = ReadReqOptionsFilterOptions()
        filter_expression = ReadReqOptionsFilterOptionsExpression()

        if isinstance(options.filter, ExcludeSystemEventsFilter):
            filter_expression.regex = "^[^\\$].*"
        else:
            if options.filter.regex:
                filter_expression.regex = options.filter.regex
            if options.filter.prefix:
                filter_expression.prefix = options.filter.prefix

        if isinstance(options.filter, ExcludeSystemEventsFilter):
            request_options.filter.event_type = filter_expression
        elif isinstance(options.filter, EventTypeFilter):
            request_options.filter.event_type = filter_expression
        elif isinstance(options.filter, StreamNameFilter):
            request_options.filter.stream_identifier = filter_expression

        if options.max_search_window is not None:
            request_options.filter.max = options.max_search_window
        else:
            request_options.filter.count = Empty()

        request_options.filter.checkpoint_interval_multiplier = (
            options.checkpoint_interval
        )

    return ReadReq(options=request_options)


def convert_read_response_confirmation(
    message: ReadRespSubscriptionConfirmation,
) -> SubscriptionConfirmation:
    return SubscriptionConfirmation(id=UUID(message.subscription_id))
