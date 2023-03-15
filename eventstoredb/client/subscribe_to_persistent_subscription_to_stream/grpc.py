from __future__ import annotations

from typing import Type
from uuid import UUID

import betterproto

from eventstoredb.client.subscribe_to_persistent_subscription_to_stream.types import (
    NackAction,
    PersistentSubscriptionConfirmation,
    SubscribeToPersistentSubscriptionToStreamOptions,
)
from eventstoredb.events import (
    BinaryRecordedEvent,
    ContentType,
    JsonRecordedEvent,
    PersistentSubscriptionEvent,
)
from eventstoredb.generated.event_store.client import Empty, StreamIdentifier, Uuid
from eventstoredb.generated.event_store.client.persistent_subscriptions import (
    ReadReq,
    ReadReqAck,
    ReadReqNack,
    ReadReqNackAction,
    ReadReqOptions,
    ReadReqOptionsUuidOption,
    ReadResp,
    ReadRespReadEvent,
    ReadRespReadEventRecordedEvent,
    ReadRespSubscriptionConfirmation,
)
from eventstoredb.types import AllPosition


def get_original_event_id(event: PersistentSubscriptionEvent) -> UUID | None:
    if event.link:
        return event.link.id
    elif event.event:
        return event.event.id
    else:
        return None


def create_read_request(
    stream_name: str,
    group_name: str,
    options: SubscribeToPersistentSubscriptionToStreamOptions,
) -> ReadReq:
    request_options = ReadReqOptions()
    request_options.stream_identifier = StreamIdentifier(stream_name.encode())
    request_options.group_name = group_name
    request_options.buffer_size = options.buffer_size
    request_options.uuid_option = ReadReqOptionsUuidOption(string=Empty())
    return ReadReq(options=request_options)


def create_ack_request(
    events: PersistentSubscriptionEvent | list[PersistentSubscriptionEvent],
) -> ReadReq:
    if not isinstance(events, list):
        events = [events]

    ack = ReadReqAck()
    for event in events:
        event_id = get_original_event_id(event)
        if event_id:
            ack.ids.append(Uuid(string=str(event_id)))
    return ReadReq(ack=ack)


def create_nack_request(
    action: NackAction,
    reason: str,
    events: PersistentSubscriptionEvent | list[PersistentSubscriptionEvent],
) -> ReadReq:
    if not isinstance(events, list):
        events = [events]

    nack = ReadReqNack()
    nack.reason = reason

    if action == NackAction.PARK:
        nack.action = ReadReqNackAction.Park
    elif action == NackAction.RETRY:
        nack.action = ReadReqNackAction.Retry
    elif action == NackAction.SKIP:
        nack.action = ReadReqNackAction.Skip
    elif action == NackAction.STOP:
        nack.action = ReadReqNackAction.Stop
    elif action == NackAction.UNKNOWN:
        nack.action = ReadReqNackAction.Unknown

    for event in events:
        event_id = get_original_event_id(event)
        if event_id:
            nack.ids.append(Uuid(string=str(event_id)))
    return ReadReq(nack=nack)


def convert_read_response(
    message: ReadResp,
) -> PersistentSubscriptionConfirmation | PersistentSubscriptionEvent:
    content_type, _ = betterproto.which_one_of(message, "content")
    if content_type == "event":
        return convert_read_response_event(message.event)
    elif content_type == "subscription_confirmation":
        return convert_read_response_confirmation(message.subscription_confirmation)
    else:
        # TODO raise better exception
        raise Exception("shouldnt be here")


def convert_read_response_event(
    message: ReadRespReadEvent,
) -> PersistentSubscriptionEvent:
    event = PersistentSubscriptionEvent()
    if message.event:
        event.event = convert_read_response_recorded_event(message.event)
    if message.link:
        event.link = convert_read_response_recorded_event(message.link)
    if message.commit_position:
        event.commit_position = message.commit_position
    if message.retry_count:
        event.retry_count = message.retry_count
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


def convert_read_response_confirmation(
    message: ReadRespSubscriptionConfirmation,
) -> PersistentSubscriptionConfirmation:
    return PersistentSubscriptionConfirmation(id=message.subscription_id)
