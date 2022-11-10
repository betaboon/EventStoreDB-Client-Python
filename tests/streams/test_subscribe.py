import asyncio
from typing import AsyncGenerator

import pytest
from pytest_mock import MockerFixture

from eventstoredb import Client
from eventstoredb.events import JsonEvent
from eventstoredb.streams.subscribe import SubscribeToStreamOptions
from eventstoredb.streams.types import StreamPosition

from ..utils import Subscriber, json_test_events


@pytest.fixture
async def subscriber(
    event_loop: asyncio.AbstractEventLoop,
    mocker: MockerFixture,
) -> AsyncGenerator[Subscriber, None]:
    s = Subscriber(event_loop)
    s.event_handler = mocker.stub()
    yield s
    await s._stop()


async def test_subscribe_to_stream_json(
    eventstoredb_client: Client,
    stream_name: str,
    subscriber: Subscriber,
) -> None:
    subscription = eventstoredb_client.subscribe_to_stream(stream_name=stream_name)

    subscriber.subscription = subscription

    assert subscriber.event_handler.call_count == 0

    await eventstoredb_client.append_to_stream(
        stream_name=stream_name,
        events=JsonEvent(type="Test"),
    )

    await asyncio.sleep(0.1)
    assert subscriber.event_handler.call_count == 1


async def test_subscribe_to_stream_from_start(
    eventstoredb_client: Client,
    stream_name: str,
    subscriber: Subscriber,
) -> None:
    await eventstoredb_client.append_to_stream(
        stream_name=stream_name,
        events=json_test_events(4),
    )

    subscription = eventstoredb_client.subscribe_to_stream(
        stream_name=stream_name,
        options=SubscribeToStreamOptions(from_revision=StreamPosition.START),
    )

    subscriber.subscription = subscription

    await asyncio.sleep(0.1)
    assert subscriber.event_handler.call_count == 4

    await eventstoredb_client.append_to_stream(
        stream_name=stream_name,
        events=JsonEvent(type="Test"),
    )

    await asyncio.sleep(0.1)
    assert subscriber.event_handler.call_count == 5


async def test_subscribe_to_stream_from_end(
    eventstoredb_client: Client,
    stream_name: str,
    subscriber: Subscriber,
) -> None:
    await eventstoredb_client.append_to_stream(
        stream_name=stream_name,
        events=json_test_events(4),
    )

    subscription = eventstoredb_client.subscribe_to_stream(
        stream_name=stream_name,
        options=SubscribeToStreamOptions(from_revision=StreamPosition.END),
    )

    subscriber.subscription = subscription

    await asyncio.sleep(0.1)
    assert subscriber.event_handler.call_count == 0

    await eventstoredb_client.append_to_stream(
        stream_name=stream_name,
        events=JsonEvent(type="Test"),
    )

    await asyncio.sleep(0.1)
    assert subscriber.event_handler.call_count == 1


async def test_subscribe_to_stream_from_revision(
    eventstoredb_client: Client,
    stream_name: str,
    subscriber: Subscriber,
) -> None:
    await eventstoredb_client.append_to_stream(
        stream_name=stream_name,
        events=json_test_events(4),
    )

    subscription = eventstoredb_client.subscribe_to_stream(
        stream_name=stream_name,
        options=SubscribeToStreamOptions(from_revision=2),
    )

    subscriber.subscription = subscription

    await asyncio.sleep(0.1)
    assert subscriber.event_handler.call_count == 1

    await eventstoredb_client.append_to_stream(
        stream_name=stream_name,
        events=JsonEvent(type="Test"),
    )

    await asyncio.sleep(0.1)
    assert subscriber.event_handler.call_count == 2
