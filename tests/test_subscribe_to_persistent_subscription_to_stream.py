import asyncio

import pytest
from pytest_mock import MockerFixture

from eventstoredb import Client
from eventstoredb.events import PersistentSubscriptionEvent
from eventstoredb.options import (
    CreatePersistentSubscriptionToStreamOptions,
    StreamPosition,
)

from .utils import Consumer, json_test_events


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


@pytest.mark.skip(reason="test not implemented")
async def test_subscribe_persistent_subscription_to_stream_nack() -> None:
    pass


@pytest.mark.skip(reason="test not implemented")
async def test_subscribe_persistent_subscription_to_stream_raises_if_not_exist() -> None:  # noqa: E501
    pass
