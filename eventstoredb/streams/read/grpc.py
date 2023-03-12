from __future__ import annotations

from typing import Type
from uuid import UUID

import betterproto

from eventstoredb.events import (
    BinaryRecordedEvent,
    ContentType,
    JsonRecordedEvent,
    ReadEvent,
)
from eventstoredb.generated.event_store.client import Empty, StreamIdentifier
from eventstoredb.generated.event_store.client.streams import (
    ReadReq,
    ReadReqOptions,
    ReadReqOptionsAllOptions,
    ReadReqOptionsFilterOptions,
    ReadReqOptionsFilterOptionsExpression,
    ReadReqOptionsPosition,
    ReadReqOptionsReadDirection,
    ReadReqOptionsStreamOptions,
    ReadReqOptionsUuidOption,
    ReadResp,
    ReadRespReadEvent,
    ReadRespReadEventRecordedEvent,
)
from eventstoredb.streams.read.exceptions import StreamNotFoundError
from eventstoredb.streams.read.types import (
    EventTypeFilter,
    ExcludeSystemEventsFilter,
    ReadAllOptions,
    ReadDirection,
    ReadStreamOptions,
    StreamNameFilter,
)
from eventstoredb.streams.types import StreamPosition, StreamRevision
from eventstoredb.types import Position


def create_read_request_options_common(
    options: ReadAllOptions | ReadStreamOptions,
) -> ReadReqOptions:
    request_options = ReadReqOptions()

    request_options.resolve_links = options.resolve_links
    request_options.count = options.max_count
    request_options.uuid_option = ReadReqOptionsUuidOption(string=Empty())

    if options.direction == ReadDirection.FORWARDS:
        request_options.read_direction = ReadReqOptionsReadDirection.Forwards
    elif options.direction == ReadDirection.BACKWARDS:
        request_options.read_direction = ReadReqOptionsReadDirection.Backwards

    return request_options


def create_read_request(
    stream_name: str,
    options: ReadStreamOptions | None = None,
) -> ReadReq:
    if options is None:
        options = ReadStreamOptions()

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


def create_read_all_request(options: ReadAllOptions | None = None) -> ReadReq:
    if options is None:
        options = ReadAllOptions()

    request_options = create_read_request_options_common(options)

    request_options.all = ReadReqOptionsAllOptions()

    if isinstance(options.from_position, Position):
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


def convert_read_response(message: ReadResp) -> ReadEvent:
    content_type, _ = betterproto.which_one_of(message, "content")
    if content_type == "stream_not_found":
        raise StreamNotFoundError(
            stream_name=message.stream_not_found.stream_identifier.stream_name.decode()
        )
    elif content_type == "event":
        return convert_read_response_read_event(message.event)
    else:
        # FIXME maybe we should raise something like "UnexpectedRuntimeError" here?
        raise Exception("i shouldnt be here")


def convert_read_response_read_event(message: ReadRespReadEvent) -> ReadEvent:
    event = ReadEvent()
    if message.event:
        event.event = convert_read_response_recorded_event(message.event)
    if message.link:
        event.link = convert_read_response_recorded_event(message.link)
    # TODO should this use which_one_of?
    if message.commit_position:
        event.commit_position = message.commit_position
    return event


def convert_read_response_recorded_event(
    message: ReadRespReadEventRecordedEvent,
) -> JsonRecordedEvent | BinaryRecordedEvent:
    stream_name = message.stream_identifier.stream_name.decode()
    id = UUID(message.id.string)
    content_type = ContentType(message.metadata["content-type"])
    position = Position(
        commit_position=message.commit_position,
        prepare_position=message.prepare_position,
    )
    event_class: Type[JsonRecordedEvent] | Type[BinaryRecordedEvent]
    if content_type == ContentType.JSON:
        event_class = JsonRecordedEvent
    else:
        event_class = BinaryRecordedEvent
    return event_class(
        stream_name=stream_name,
        id=id,
        revision=message.stream_revision,
        type=message.metadata["type"],
        content_type=content_type,
        created=int(message.metadata["created"]),
        position=position,
        data=message.data if message.data else None,
        metadata=message.custom_metadata if message.custom_metadata else None,
    )
