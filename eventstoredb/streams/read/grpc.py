from __future__ import annotations

from typing import Type
from uuid import UUID

import betterproto

from eventstoredb.events import (
    BinaryRecordedEvent,
    ContentType,
    JsonRecordedEvent,
    Position,
    ReadEvent,
)
from eventstoredb.generated.event_store.client import Empty, StreamIdentifier
from eventstoredb.generated.event_store.client.streams import (
    ReadReqOptions,
    ReadReqOptionsReadDirection,
    ReadReqOptionsStreamOptions,
    ReadReqOptionsUuidOption,
    ReadResp,
    ReadRespReadEvent,
    ReadRespReadEventRecordedEvent,
)
from eventstoredb.streams.read.exceptions import StreamNotFoundError
from eventstoredb.streams.read.types import ReadDirection, ReadStreamOptions
from eventstoredb.streams.types import StreamPosition, StreamRevision


def create_read_request_options(
    stream_name: str,
    options: ReadStreamOptions | None = None,
) -> ReadReqOptions:
    if options is None:
        options = ReadStreamOptions()

    request_options = ReadReqOptions()
    request_options.resolve_links = options.resolve_links
    request_options.count = options.max_count
    request_options.no_filter = Empty()
    request_options.uuid_option = ReadReqOptionsUuidOption(string=Empty())

    if options.direction == ReadDirection.FORWARDS:
        request_options.read_direction = ReadReqOptionsReadDirection.Forwards
    elif options.direction == ReadDirection.BACKWARDS:
        request_options.read_direction = ReadReqOptionsReadDirection.Backwards

    request_options.stream = ReadReqOptionsStreamOptions()
    request_options.stream.stream_identifier = StreamIdentifier(stream_name.encode())

    if isinstance(options.from_revision, StreamRevision):
        request_options.stream.revision = options.from_revision
    elif options.from_revision == StreamPosition.START:
        request_options.stream.start = Empty()
    elif options.from_revision == StreamPosition.END:
        request_options.stream.end = Empty()

    return request_options


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
        commit=message.commit_position,
        prepare=message.prepare_position,
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
