from __future__ import annotations

import betterproto

from eventstoredb.client.read_stream.grpc import convert_read_response
from eventstoredb.client.subscribe_to_stream.types import (
    SubscribeToStreamOptions,
    SubscriptionConfirmation,
)
from eventstoredb.events import CaughtUp, FellBehind, ReadEvent
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
from eventstoredb.types import StreamPosition, StreamRevision


def create_subscribe_to_stream_request(
    stream_name: str,
    options: SubscribeToStreamOptions,
) -> ReadReq:
    request_options = ReadReqOptions()
    request_options.resolve_links = options.resolve_links
    request_options.uuid_option = ReadReqOptionsUuidOption(string=Empty())
    request_options.subscription = ReadReqOptionsSubscriptionOptions()
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


def convert_subscribe_to_stream_response(
    message: ReadResp,
) -> ReadEvent | CaughtUp | FellBehind | SubscriptionConfirmation:
    content_type, _ = betterproto.which_one_of(message, "content")

    if content_type == "confirmation":
        return convert_read_response_subscription_confirmation(message.confirmation)
    else:
        return convert_read_response(message)


def convert_read_response_subscription_confirmation(
    message: ReadRespSubscriptionConfirmation,
) -> SubscriptionConfirmation:
    return SubscriptionConfirmation(id=message.subscription_id)
