import asyncio

import pytest
from pytest_mock import MockerFixture

from eventstoredb import Client
from eventstoredb.persistent_subscriptions.create.types import (
    CreatePersistentSubscriptionOptions,
)
from eventstoredb.persistent_subscriptions.subscribe.types import (
    PersistentSubscriptionEvent,
)
from eventstoredb.streams.types import StreamPosition
from ..utils import json_test_events, PersistentSubscriber

pytestmark = pytest.mark.asyncio


@pytest.fixture
async def subscriber(event_loop):
    s = PersistentSubscriber(event_loop)
    yield s
    await s._stop()


async def test_subscribe_persistent_subscription_from_start(
    eventstoredb_client: Client,
    stream_name: str,
    group_name: str,
    subscriber: PersistentSubscriber,
    mocker: MockerFixture,
):
    await eventstoredb_client.append_to_stream(
        stream_name=stream_name,
        events=json_test_events(10),
    )
    await eventstoredb_client.create_persistent_subscription(
        stream_name=stream_name,
        group_name=group_name,
        options=CreatePersistentSubscriptionOptions(from_revision=StreamPosition.START),
    )

    subscription = eventstoredb_client.subscribe_to_persistent_subscription(
        stream_name=stream_name,
        group_name=group_name,
    )

    handler_stub = mocker.stub()

    async def handler(event: PersistentSubscriptionEvent) -> None:
        await subscription.ack(event)
        handler_stub(event)

    subscriber.subscription = subscription
    subscriber.event_handler = handler

    await asyncio.sleep(0.1)
    assert handler_stub.call_count == 10

    await eventstoredb_client.append_to_stream(
        stream_name=stream_name,
        events=json_test_events(10),
    )

    await asyncio.sleep(0.1)
    assert handler_stub.call_count == 20


@pytest.mark.skip(reason="test not implemented")
async def test_subscribe_persistent_subscription_from_end():
    pass


@pytest.mark.skip(reason="test not implemented")
async def test_subscribe_persistent_subscription_from_revision():
    pass


@pytest.mark.skip(reason="test not implemented")
async def test_subscribe_persistent_subscription_nack():
    pass


@pytest.mark.skip(reason="test not implemented")
async def test_subscribe_persistent_subscription_raises_if_not_exist():
    pass
