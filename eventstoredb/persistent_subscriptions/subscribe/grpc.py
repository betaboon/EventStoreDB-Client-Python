import json
from typing import List, Optional, Union
from uuid import UUID

import betterproto

from eventstoredb.events import (
    BinaryRecordedEvent,
    ContentType,
    JsonRecordedEvent,
    Position,
    RecordedEvent,
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
from eventstoredb.persistent_subscriptions.subscribe.types import (
    NackAction,
    PersistentSubscriptionConfirmation,
    PersistentSubscriptionEvent,
    SubscribeToPersistentSubscriptionOptions,
)


def create_read_request(
    stream_name: str,
    group_name: str,
    options: Optional[SubscribeToPersistentSubscriptionOptions] = None,
) -> ReadReq:
    if options is None:
        options = SubscribeToPersistentSubscriptionOptions()

    request_options = ReadReqOptions()
    request_options.stream_identifier = StreamIdentifier(stream_name.encode())
    request_options.group_name = group_name
    request_options.buffer_size = options.buffer_size
    request_options.uuid_option = ReadReqOptionsUuidOption(string=Empty())

    return ReadReq(options=request_options)


def create_ack_request(
    events: Union[List[PersistentSubscriptionEvent], PersistentSubscriptionEvent]
) -> ReadReq:
    if not isinstance(events, List):
        events = [events]

    ack = ReadReqAck()
    for event in events:
        ack.ids.append(Uuid(string=str(event.original_id)))
    return ReadReq(ack=ack)


def create_nack_request(
    action: NackAction,
    reason: str,
    events: Union[List[PersistentSubscriptionEvent], PersistentSubscriptionEvent],
) -> ReadReq:
    if not isinstance(events, List):
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
        nack.ids.append(Uuid(string=str(event.original_id)))
    return ReadReq(nack=nack)


def convert_read_response(
    message: ReadResp,
) -> Union[PersistentSubscriptionConfirmation, PersistentSubscriptionEvent]:
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
) -> Union[JsonRecordedEvent, BinaryRecordedEvent]:
    stream_name = message.stream_identifier.stream_name.decode()
    id = UUID(message.id.string)
    content_type = ContentType(message.metadata["content-type"])
    position = Position(
        commit=message.commit_position,
        prepare=message.prepare_position,
    )
    data = message.data
    metadata = message.custom_metadata
    # TODO reduce duplication
    if content_type == ContentType.JSON:
        data = json.loads(data.decode()) if data else None
        metadata = json.loads(metadata.decode()) if metadata else None
        return JsonRecordedEvent(
            stream_name=stream_name,
            id=id,
            revision=message.stream_revision,
            type=message.metadata["type"],
            content_type=content_type,
            created=int(message.metadata["created"]),
            position=position,
            data=data,
            metadata=metadata,
        )
    return BinaryRecordedEvent(
        stream_name=stream_name,
        id=id,
        revision=message.stream_revision,
        type=message.metadata["type"],
        content_type=content_type,
        created=int(message.metadata["created"]),
        position=position,
        data=data,
        metadata=metadata,
    )


def convert_read_response_confirmation(
    message: ReadRespSubscriptionConfirmation,
) -> PersistentSubscriptionConfirmation:
    return PersistentSubscriptionConfirmation(id=message.subscription_id)
