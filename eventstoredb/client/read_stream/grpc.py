from __future__ import annotations

from typing import Type
from uuid import UUID

import betterproto

from eventstoredb.client.exceptions import StreamNotFoundError
from eventstoredb.client.read_stream.types import ReadStreamOptions
from eventstoredb.events import (
    BinaryRecordedEvent,
    CaughtUp,
    ContentType,
    FellBehind,
    JsonRecordedEvent,
    ReadEvent,
)
from eventstoredb.generated.event_store.client import Empty, StreamIdentifier
from eventstoredb.generated.event_store.client.streams import (
    ReadReq,
    ReadReqOptions,
    ReadReqOptionsReadDirection,
    ReadReqOptionsStreamOptions,
    ReadReqOptionsUuidOption,
    ReadResp,
    ReadRespReadEvent,
    ReadRespReadEventRecordedEvent,
)
from eventstoredb.types import (
    AllPosition,
    ReadDirection,
    StreamPosition,
    StreamRevision,
)


def create_read_request(stream_name: str, options: ReadStreamOptions) -> ReadReq:
    request_options = ReadReqOptions()

    request_options.resolve_links = options.resolve_links
    request_options.count = options.max_count
    request_options.uuid_option = ReadReqOptionsUuidOption(string=Empty())

    if options.direction == ReadDirection.FORWARDS:
        request_options.read_direction = ReadReqOptionsReadDirection.Forwards  # type: ignore
    elif options.direction == ReadDirection.BACKWARDS:
        request_options.read_direction = ReadReqOptionsReadDirection.Backwards  # type: ignore

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


def convert_read_response(message: ReadResp) -> ReadEvent | CaughtUp | FellBehind:
    content_type, _ = betterproto.which_one_of(message, "content")
    if content_type == "event":
        return convert_read_response_read_event(message.event)
    elif content_type == "caught_up":
        return CaughtUp()
    elif content_type == "fell_behind":
        return FellBehind()
    elif content_type == "stream_not_found":
        raise StreamNotFoundError(
            stream_name=message.stream_not_found.stream_identifier.stream_name.decode()
        )
    else:
        # FIXME maybe we should raise something like "UnexpectedRuntimeError" here?
        raise Exception(f"i shouldnt be here {content_type=} {message=}")


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
    position = AllPosition(
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
