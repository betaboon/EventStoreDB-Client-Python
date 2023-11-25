from uuid import uuid4

import pytest

from eventstoredb import Client
from eventstoredb.events import JsonEvent, PersistentSubscriptionEvent
from eventstoredb.exceptions import PersistentSubscriptionNotFoundError
from eventstoredb.filters import EventTypeFilter, StreamNameFilter
from eventstoredb.options import (
    CreatePersistentSubscriptionToAllOptions,
    StreamPosition,
)

from .utils import Consumer


async def test_subscribe_persistent_subscription_to_all(
    eventstoredb_client: Client,
    stream_name: str,
    group_name: str,
) -> None:
    await eventstoredb_client.create_persistent_subscription_to_all(
        group_name=group_name
    )

    subscription = eventstoredb_client.subscribe_to_persistent_subscription_to_all(
        group_name=group_name,
    )

    async def on_event(event: PersistentSubscriptionEvent) -> None:
        await subscription.ack(event)

    consumer = Consumer(subscription, on_event=on_event)
    await consumer.start()

    await eventstoredb_client.append_to_stream(
        stream_name=stream_name,
        events=[JsonEvent(type="test_subscribe_persistent_subscription_to_all_Test")],
    )

    await consumer.stop(1)

    read_events = [e for e in consumer.events if type(e) is PersistentSubscriptionEvent]
    events = [
        e
        for e in read_events
        if e.event is not None
        and e.event.type.startswith("test_subscribe_persistent_subscription_to_all_")
    ]

    assert len(events) == 1
    assert events[0].event is not None
    event = events[0].event
    assert event.stream_name == stream_name
    assert event.type == "test_subscribe_persistent_subscription_to_all_Test"


async def test_subscribe_persistent_subscription_to_all_raises_if_not_exist(
    eventstoredb_client: Client,
    group_name: str,
) -> None:
    with pytest.raises(PersistentSubscriptionNotFoundError):
        subscription = eventstoredb_client.subscribe_to_persistent_subscription_to_all(
            group_name=group_name,
        )
        consumer = Consumer(subscription)
        await consumer.run_for(1)


@pytest.mark.skip(reason="test not implemented")
async def test_subscribe_persistent_subscription_to_all_nack() -> None:
    pass


async def test_subscribe_persistent_subscription_to_all_from_start(
    eventstoredb_client: Client,
    group_name: str,
) -> None:
    stream_name_1 = f"Test1-{uuid4()}"
    stream_name_2 = f"Test2-{uuid4()}"

    await eventstoredb_client.append_to_stream(
        stream_name=stream_name_1,
        events=[
            JsonEvent(
                type="test_subscribe_persistent_subscription_to_all_from_start_Test1"
            )
        ],
    )

    await eventstoredb_client.create_persistent_subscription_to_all(
        group_name=group_name,
        options=CreatePersistentSubscriptionToAllOptions(
            from_position=StreamPosition.START
        ),
    )

    subscription = eventstoredb_client.subscribe_to_persistent_subscription_to_all(
        group_name=group_name,
    )

    async def on_event(event: PersistentSubscriptionEvent) -> None:
        await subscription.ack(event)

    consumer = Consumer(subscription, on_event=on_event)
    await consumer.start()

    await eventstoredb_client.append_to_stream(
        stream_name=stream_name_2,
        events=[
            JsonEvent(
                type="test_subscribe_persistent_subscription_to_all_from_start_Test2"
            )
        ],
    )

    await consumer.stop(1)

    read_events = [e for e in consumer.events if type(e) is PersistentSubscriptionEvent]
    events = [
        e
        for e in read_events
        if e.event is not None
        and e.event.type.startswith(
            "test_subscribe_persistent_subscription_to_all_from_start_"
        )
    ]

    assert len(events) == 2

    assert events[0].event is not None
    event = events[0].event
    assert event.stream_name == stream_name_1
    assert (
        event.type == "test_subscribe_persistent_subscription_to_all_from_start_Test1"
    )

    assert events[1].event is not None
    event = events[1].event
    assert event.stream_name == stream_name_2
    assert (
        event.type == "test_subscribe_persistent_subscription_to_all_from_start_Test2"
    )


async def test_subscribe_persistent_subscription_to_all_from_end(
    eventstoredb_client: Client,
    group_name: str,
) -> None:
    stream_name_1 = f"Test1-{uuid4()}"
    stream_name_2 = f"Test2-{uuid4()}"

    await eventstoredb_client.append_to_stream(
        stream_name=stream_name_1,
        events=[
            JsonEvent(
                type="test_subscribe_persistent_subscription_to_all_from_end_Test1"
            )
        ],
    )

    await eventstoredb_client.create_persistent_subscription_to_all(
        group_name=group_name,
        options=CreatePersistentSubscriptionToAllOptions(
            from_position=StreamPosition.END
        ),
    )

    subscription = eventstoredb_client.subscribe_to_persistent_subscription_to_all(
        group_name=group_name,
    )

    async def on_event(event: PersistentSubscriptionEvent) -> None:
        await subscription.ack(event)

    consumer = Consumer(subscription, on_event=on_event)
    await consumer.start()

    await eventstoredb_client.append_to_stream(
        stream_name=stream_name_2,
        events=[
            JsonEvent(
                type="test_subscribe_persistent_subscription_to_all_from_end_Test2"
            )
        ],
    )

    await consumer.stop(1)

    read_events = [e for e in consumer.events if type(e) is PersistentSubscriptionEvent]
    events = [
        e
        for e in read_events
        if e.event is not None
        and e.event.type.startswith(
            "test_subscribe_persistent_subscription_to_all_from_end_"
        )
    ]

    assert len(events) == 1

    assert events[0].event is not None
    event = events[0].event
    assert event.stream_name == stream_name_2
    assert event.type == "test_subscribe_persistent_subscription_to_all_from_end_Test2"


async def test_subscribe_persistent_subscription_to_all_from_position(
    eventstoredb_client: Client,
    stream_name: str,
    group_name: str,
) -> None:
    await eventstoredb_client.append_to_stream(
        stream_name=stream_name,
        events=[JsonEvent(type="Junk")],
    )

    marker = await eventstoredb_client.append_to_stream(
        stream_name=stream_name,
        events=[JsonEvent(type="Marker")],
    )
    assert marker.position is not None

    await eventstoredb_client.append_to_stream(
        stream_name=stream_name,
        events=[JsonEvent(type="Test")],
    )

    await eventstoredb_client.create_persistent_subscription_to_all(
        group_name=group_name,
        options=CreatePersistentSubscriptionToAllOptions(from_position=marker.position),
    )

    subscription = eventstoredb_client.subscribe_to_persistent_subscription_to_all(
        group_name=group_name,
    )

    async def on_event(event: PersistentSubscriptionEvent) -> None:
        await subscription.ack(event)

    consumer = Consumer(subscription, on_event=on_event)
    await consumer.run_for(1)

    read_events = [e for e in consumer.events if type(e) is PersistentSubscriptionEvent]
    events = [
        e
        for e in read_events
        if e.event is not None and not e.event.stream_name.startswith("$")
    ]

    assert len(events) == 2

    assert events[0].event is not None
    event = events[0].event
    assert event.stream_name == stream_name
    assert event.type == "Marker"

    assert events[1].event is not None
    event = events[1].event
    assert event.stream_name == stream_name
    assert event.type == "Test"


async def test_subscribe_persistent_subscription_to_all_filter_by_event_type_regex(
    eventstoredb_client: Client,
    stream_name: str,
    group_name: str,
) -> None:
    await eventstoredb_client.append_to_stream(
        stream_name=stream_name,
        events=[
            JsonEvent(
                type="persistent_subscription_to_all_filter_by_event_type_regex_Test1"
            ),
            JsonEvent(
                type="persistent_subscription_to_all_filter_by_event_type_regex_Test2"
            ),
        ],
    )

    await eventstoredb_client.create_persistent_subscription_to_all(
        group_name=group_name,
        options=CreatePersistentSubscriptionToAllOptions(
            filter=EventTypeFilter(
                regex="persistent_subscription_to_all_filter_by_event_type_regex_Test1"
            )
        ),
    )

    subscription = eventstoredb_client.subscribe_to_persistent_subscription_to_all(
        group_name=group_name,
    )

    async def on_event(event: PersistentSubscriptionEvent) -> None:
        await subscription.ack(event)

    consumer = Consumer(subscription, on_event=on_event)
    await consumer.run_for(1)

    read_events = [e for e in consumer.events if type(e) is PersistentSubscriptionEvent]
    events = [e for e in read_events]

    assert len(events) == 1
    assert events[0].event is not None
    event = events[0].event
    assert event.stream_name == stream_name
    assert (
        event.type == "persistent_subscription_to_all_filter_by_event_type_regex_Test1"
    )


async def test_subscribe_persistent_subscription_to_all_filter_by_event_type_prefix(
    eventstoredb_client: Client,
    stream_name: str,
    group_name: str,
) -> None:
    await eventstoredb_client.append_to_stream(
        stream_name=stream_name,
        events=[
            JsonEvent(
                type="persistent_subscription_to_all_filter_by_event_type_prefix_Test1"
            ),
            JsonEvent(
                type="persistent_subscription_to_all_filter_by_event_type_prefix_Test2"
            ),
        ],
    )

    await eventstoredb_client.create_persistent_subscription_to_all(
        group_name=group_name,
        options=CreatePersistentSubscriptionToAllOptions(
            filter=EventTypeFilter(
                prefix=["persistent_subscription_to_all_filter_by_event_type_prefix_"]
            )
        ),
    )

    subscription = eventstoredb_client.subscribe_to_persistent_subscription_to_all(
        group_name=group_name,
    )

    async def on_event(event: PersistentSubscriptionEvent) -> None:
        await subscription.ack(event)

    consumer = Consumer(subscription, on_event=on_event)
    await consumer.run_for(1)

    read_events = [e for e in consumer.events if type(e) is PersistentSubscriptionEvent]
    events = [e for e in read_events]

    assert len(events) == 2

    assert events[0].event is not None
    event = events[0].event
    assert event.stream_name == stream_name
    assert (
        event.type == "persistent_subscription_to_all_filter_by_event_type_prefix_Test1"
    )

    assert events[1].event is not None
    event = events[1].event
    assert event.stream_name == stream_name
    assert (
        event.type == "persistent_subscription_to_all_filter_by_event_type_prefix_Test2"
    )


async def test_subscribe_persistent_subscription_to_all_filter_by_stream_name_regex(
    eventstoredb_client: Client,
    group_name: str,
) -> None:
    stream_name_1 = (
        f"persistent_subscription_to_all_filter_by_stream_name_regex_Test1-{uuid4()}"
    )
    stream_name_2 = (
        f"persistent_subscription_to_all_filter_by_stream_name_regex_Test2-{uuid4()}"
    )

    await eventstoredb_client.append_to_stream(
        stream_name=stream_name_1,
        events=[JsonEvent(type="Test")],
    )
    await eventstoredb_client.append_to_stream(
        stream_name=stream_name_2,
        events=[JsonEvent(type="Test")],
    )

    await eventstoredb_client.create_persistent_subscription_to_all(
        group_name=group_name,
        options=CreatePersistentSubscriptionToAllOptions(
            filter=StreamNameFilter(regex=stream_name_1)
        ),
    )

    subscription = eventstoredb_client.subscribe_to_persistent_subscription_to_all(
        group_name=group_name,
    )

    async def on_event(event: PersistentSubscriptionEvent) -> None:
        await subscription.ack(event)

    consumer = Consumer(subscription, on_event=on_event)
    await consumer.run_for(1)

    read_events = [e for e in consumer.events if type(e) is PersistentSubscriptionEvent]
    events = [e for e in read_events]

    assert len(events) == 1
    assert events[0].event is not None
    event = events[0].event
    assert event.stream_name == stream_name_1
    assert event.type == "Test"


async def test_subscribe_persistent_subscription_to_all_filter_by_stream_name_prefix(
    eventstoredb_client: Client,
    group_name: str,
) -> None:
    stream_name_1 = (
        f"persistent_subscription_to_all_filter_by_stream_name_prefix_Test1-{uuid4()}"
    )
    stream_name_2 = (
        f"persistent_subscription_to_all_filter_by_stream_name_prefix_Test2-{uuid4()}"
    )

    await eventstoredb_client.append_to_stream(
        stream_name=stream_name_1,
        events=[JsonEvent(type="Test")],
    )
    await eventstoredb_client.append_to_stream(
        stream_name=stream_name_2,
        events=[JsonEvent(type="Test")],
    )

    await eventstoredb_client.create_persistent_subscription_to_all(
        group_name=group_name,
        options=CreatePersistentSubscriptionToAllOptions(
            filter=StreamNameFilter(
                prefix=["persistent_subscription_to_all_filter_by_stream_name_prefix_"]
            )
        ),
    )

    subscription = eventstoredb_client.subscribe_to_persistent_subscription_to_all(
        group_name=group_name,
    )

    async def on_event(event: PersistentSubscriptionEvent) -> None:
        await subscription.ack(event)

    consumer = Consumer(subscription, on_event=on_event)
    await consumer.run_for(1)

    read_events = [e for e in consumer.events if type(e) is PersistentSubscriptionEvent]
    events = [e for e in read_events]

    assert len(events) == 2

    assert events[0].event is not None
    event = events[0].event
    assert event.stream_name == stream_name_1
    assert event.type == "Test"

    assert events[1].event is not None
    event = events[1].event
    assert event.stream_name == stream_name_2
    assert event.type == "Test"


@pytest.mark.skip(reason="test not implemented")
async def test_subscribe_persistent_subscription_to_all_exclude_System_events() -> None:
    pass
