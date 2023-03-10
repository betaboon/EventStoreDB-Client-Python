from __future__ import annotations

from uuid import UUID

import betterproto

from eventstoredb.events import ReadEvent
from eventstoredb.generated.event_store.client import Empty, StreamIdentifier
from eventstoredb.generated.event_store.client.streams import (
    ReadReq,
    ReadReqOptions,
    ReadReqOptionsStreamOptions,
    ReadReqOptionsSubscriptionOptions,
    ReadReqOptionsUuidOption,
    ReadResp,
    ReadRespSubscriptionConfirmation,
)
from eventstoredb.streams.read.grpc import convert_read_response_read_event
from eventstoredb.streams.subscribe.types import (
    SubscribeToStreamOptions,
    SubscriptionConfirmation,
)
from eventstoredb.streams.types import StreamPosition, StreamRevision


def create_subscribe_request(
    stream_name: str,
    options: SubscribeToStreamOptions | None = None,
) -> ReadReq:
    if options is None:
        options = SubscribeToStreamOptions()

    request_options = ReadReqOptions()
    request_options.resolve_links = options.resolve_links
    request_options.no_filter = Empty()
    request_options.uuid_option = ReadReqOptionsUuidOption(string=Empty())
    request_options.subscription = ReadReqOptionsSubscriptionOptions()

    request_options.stream = ReadReqOptionsStreamOptions()
    request_options.stream.stream_identifier = StreamIdentifier(stream_name.encode())

    if isinstance(options.from_revision, StreamRevision):
        request_options.stream.revision = options.from_revision
    elif options.from_revision == StreamPosition.START:
        request_options.stream.start = Empty()
    elif options.from_revision == StreamPosition.END:
        request_options.stream.end = Empty()

    return ReadReq(options=request_options)


def convert_read_response(
    message: ReadResp,
) -> SubscriptionConfirmation | ReadEvent:
    content_type, _ = betterproto.which_one_of(message, "content")
    if content_type == "event":
        return convert_read_response_read_event(message.event)
    elif content_type == "confirmation":
        return convert_read_response_confirmation(message.confirmation)
    else:
        # TODO raise better exception
        raise Exception("shouldnt be here")


def convert_read_response_confirmation(
    message: ReadRespSubscriptionConfirmation,
) -> SubscriptionConfirmation:
    return SubscriptionConfirmation(id=UUID(message.subscription_id))
