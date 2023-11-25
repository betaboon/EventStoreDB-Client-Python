from __future__ import annotations

import betterproto

from eventstoredb.client.subscribe_to_all.types import Checkpoint, SubscribeToAllOptions
from eventstoredb.client.subscribe_to_stream.grpc import (
    convert_subscribe_to_stream_response,
)
from eventstoredb.client.subscribe_to_stream.types import SubscriptionConfirmation
from eventstoredb.events import CaughtUp, FellBehind, ReadEvent
from eventstoredb.filters import (
    EventTypeFilter,
    ExcludeSystemEventsFilter,
    StreamNameFilter,
)
from eventstoredb.generated.event_store.client import Empty
from eventstoredb.generated.event_store.client.streams import (
    ReadReq,
    ReadReqOptions,
    ReadReqOptionsAllOptions,
    ReadReqOptionsFilterOptions,
    ReadReqOptionsFilterOptionsExpression,
    ReadReqOptionsPosition,
    ReadReqOptionsSubscriptionOptions,
    ReadReqOptionsUuidOption,
    ReadResp,
    ReadRespCheckpoint,
)
from eventstoredb.types import AllPosition, StreamPosition


def create_subscribe_to_all_request(options: SubscribeToAllOptions) -> ReadReq:
    request_options = ReadReqOptions()
    request_options.resolve_links = options.resolve_links
    request_options.uuid_option = ReadReqOptionsUuidOption(string=Empty())
    request_options.subscription = ReadReqOptionsSubscriptionOptions()
    request_options.all = ReadReqOptionsAllOptions()

    if isinstance(options.from_position, AllPosition):
        request_options.all.position = ReadReqOptionsPosition()
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


def convert_subscribe_to_all_response(
    message: ReadResp,
) -> ReadEvent | CaughtUp | FellBehind | SubscriptionConfirmation | Checkpoint:
    content_type, _ = betterproto.which_one_of(message, "content")

    if content_type == "checkpoint":
        return convert_read_response_checkpoint(message.checkpoint)
    else:
        return convert_subscribe_to_stream_response(message)


def convert_read_response_checkpoint(message: ReadRespCheckpoint) -> Checkpoint:
    return Checkpoint(
        commit_position=message.commit_position,
        prepare_position=message.prepare_position,
    )
