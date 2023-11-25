import asyncio

import pytest
from pytest_mock import MockerFixture

from eventstoredb import Client
from eventstoredb.events import JsonEvent, PersistentSubscriptionEvent
from eventstoredb.exceptions import PersistentSubscriptionNotFoundError
from eventstoredb.options import (
    CreatePersistentSubscriptionToStreamOptions,
    StreamPosition,
)

from .utils import Consumer, json_test_events


async def test_subscribe_persistent_subscription_to_stream(
    eventstoredb_client: Client,
    stream_name: str,
    group_name: str,
) -> None:
    await eventstoredb_client.create_persistent_subscription_to_stream(
        stream_name=stream_name,
        group_name=group_name,
    )

    subscription = eventstoredb_client.subscribe_to_persistent_subscription_to_stream(
        stream_name=stream_name,
        group_name=group_name,
    )

    async def on_event(event: PersistentSubscriptionEvent) -> None:
        await subscription.ack(event)

    consumer = Consumer(subscription, on_event=on_event)
    await consumer.start()

    await eventstoredb_client.append_to_stream(
        stream_name=stream_name,
        events=[
            JsonEvent(type="test_subscribe_persistent_subscription_to_stream_Test")
        ],
    )

    await consumer.stop(1)

    read_events = [e for e in consumer.events if type(e) is PersistentSubscriptionEvent]
    events = [
        e
        for e in read_events
        if e.event is not None
        and e.event.type.startswith("test_subscribe_persistent_subscription_to_stream_")
    ]

    assert len(events) == 1
    assert events[0].event is not None
    event = events[0].event
    assert event.stream_name == stream_name
    assert event.type == "test_subscribe_persistent_subscription_to_stream_Test"


async def test_subscribe_persistent_subscription_to_stream_raises_if_not_exist(
    eventstoredb_client: Client,
    stream_name: str,
    group_name: str,
) -> None:
    with pytest.raises(PersistentSubscriptionNotFoundError):
        subscription = (
            eventstoredb_client.subscribe_to_persistent_subscription_to_stream(
                stream_name=stream_name,
                group_name=group_name,
            )
        )
        consumer = Consumer(subscription)
        await consumer.run_for(1)


@pytest.mark.skip(reason="test not implemented")
async def test_subscribe_persistent_subscription_to_stream_nack() -> None:
    pass


async def test_subscribe_persistent_subscription_to_stream_from_start(
    eventstoredb_client: Client,
    stream_name: str,
    group_name: str,
    mocker: MockerFixture,
) -> None:
    await eventstoredb_client.append_to_stream(
        stream_name=stream_name,
        events=json_test_events(10),
    )
    await eventstoredb_client.create_persistent_subscription_to_stream(
        stream_name=stream_name,
        group_name=group_name,
        options=CreatePersistentSubscriptionToStreamOptions(
            from_revision=StreamPosition.START
        ),
    )

    subscription = eventstoredb_client.subscribe_to_persistent_subscription_to_stream(
        stream_name=stream_name,
        group_name=group_name,
    )

    async def on_event(event: PersistentSubscriptionEvent) -> None:
        await subscription.ack(event)

    consumer = Consumer(subscription, on_event=on_event)
    await consumer.start()
    await asyncio.sleep(1)

    assert len(consumer.events) == 10

    await eventstoredb_client.append_to_stream(
        stream_name=stream_name,
        events=json_test_events(10),
    )

    await consumer.stop(1)

    assert len(consumer.events) == 20


@pytest.mark.skip(reason="test not implemented")
async def test_subscribe_persistent_subscription_to_stream_from_end() -> None:
    pass


@pytest.mark.skip(reason="test not implemented")
async def test_subscribe_persistent_subscription_to_stream_from_revision() -> None:
    pass
