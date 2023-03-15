from __future__ import annotations

from eventstoredb.client.read_all.types import ReadAllOptions
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
    ReadReqOptionsReadDirection,
    ReadReqOptionsUuidOption,
)
from eventstoredb.types import AllPosition, ReadDirection, StreamPosition


def create_read_all_request(options: ReadAllOptions) -> ReadReq:
    request_options = ReadReqOptions()

    request_options.resolve_links = options.resolve_links
    request_options.count = options.max_count
    request_options.uuid_option = ReadReqOptionsUuidOption(string=Empty())

    if options.direction == ReadDirection.FORWARDS:
        request_options.read_direction = ReadReqOptionsReadDirection.Forwards
    elif options.direction == ReadDirection.BACKWARDS:
        request_options.read_direction = ReadReqOptionsReadDirection.Backwards

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

        request_options.filter.max = 0
        request_options.filter.count = Empty()

    return ReadReq(options=request_options)
