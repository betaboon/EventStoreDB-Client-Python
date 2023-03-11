import asyncio
from typing import AsyncGenerator
from uuid import uuid4

import pytest
from pytest_mock import MockerFixture

from eventstoredb import Client
from eventstoredb.events import JsonEvent
from eventstoredb.streams.subscribe import SubscribeToAllOptions
from eventstoredb.streams.types import (
    AllPosition,
    EventTypeFilter,
    ExcludeSystemEventsFilter,
    StreamNameFilter,
    StreamPosition,
)

from ..utils import Subscriber


@pytest.fixture
async def subscriber(
    event_loop: asyncio.AbstractEventLoop,
    mocker: MockerFixture,
) -> AsyncGenerator[Subscriber, None]:
    s = Subscriber(event_loop)
    s.event_handler = mocker.stub()
    yield s
    await s._stop()


async def test_subscribe_to_all(
    eventstoredb_client: Client,
    subscriber: Subscriber,
) -> None:
    subscription = eventstoredb_client.subscribe_to_all()

    subscriber.subscription = subscription

    assert subscriber.event_handler.call_count == 0

    stream_name = f"Test-{uuid4()}"

    await eventstoredb_client.append_to_stream(
        stream_name=stream_name,
        events=[JsonEvent(type="test_subscribe_to_all_Test")],
    )

    await asyncio.sleep(0.1)
    events = [c[0][0] for c in subscriber.event_handler.call_args_list]
    events = [e for e in events if e.event.type.startswith("test_subscribe_to_all_")]

    assert len(events) == 1
    assert events[0].event is not None
    event = events[0].event
    assert event.stream_name == stream_name
    assert event.type == "test_subscribe_to_all_Test"


async def test_subscribe_to_all_from_start(
    eventstoredb_client: Client,
    subscriber: Subscriber,
) -> None:
    stream_name_1 = f"Test1-{uuid4()}"
    stream_name_2 = f"Test2-{uuid4()}"

    await eventstoredb_client.append_to_stream(
        stream_name=stream_name_1,
        events=[JsonEvent(type="test_subscribe_to_all_from_start_Test1")],
    )

    subscription = eventstoredb_client.subscribe_to_all(
        options=SubscribeToAllOptions(from_position=StreamPosition.START)
    )

    subscriber.subscription = subscription

    assert subscriber.event_handler.call_count == 0

    await eventstoredb_client.append_to_stream(
        stream_name=stream_name_2,
        events=[JsonEvent(type="test_subscribe_to_all_from_start_Test2")],
    )

    await asyncio.sleep(0.1)
    events = [c[0][0] for c in subscriber.event_handler.call_args_list]
    events = [
        e
        for e in events
        if e.event.type.startswith("test_subscribe_to_all_from_start_")
    ]

    assert len(events) == 2

    assert events[0].event is not None
    event = events[0].event
    assert event.stream_name == stream_name_1
    assert event.type == "test_subscribe_to_all_from_start_Test1"

    assert events[1].event is not None
    event = events[1].event
    assert event.stream_name == stream_name_2
    assert event.type == "test_subscribe_to_all_from_start_Test2"


async def test_subscribe_to_all_from_end(
    eventstoredb_client: Client,
    subscriber: Subscriber,
) -> None:
    stream_name_1 = f"Test1-{uuid4()}"
    stream_name_2 = f"Test2-{uuid4()}"

    await eventstoredb_client.append_to_stream(
        stream_name=stream_name_1,
        events=[JsonEvent(type="test_subscribe_to_all_from_end_Test1")],
    )

    subscription = eventstoredb_client.subscribe_to_all(
        options=SubscribeToAllOptions(from_position=StreamPosition.END)
    )

    subscriber.subscription = subscription

    assert subscriber.event_handler.call_count == 0
    await asyncio.sleep(0.1)

    await eventstoredb_client.append_to_stream(
        stream_name=stream_name_2,
        events=[JsonEvent(type="test_subscribe_to_all_from_end_Test2")],
    )

    await asyncio.sleep(0.1)
    events = [c[0][0] for c in subscriber.event_handler.call_args_list]
    events = [
        e for e in events if e.event.type.startswith("test_subscribe_to_all_from_end_")
    ]

    assert len(events) == 1
    assert events[0].event is not None
    event = events[0].event
    assert event.stream_name == stream_name_2
    assert event.type == "test_subscribe_to_all_from_end_Test2"


async def test_subscribe_to_all_from_position(
    eventstoredb_client: Client,
    subscriber: Subscriber,
) -> None:
    stream_name = f"Test-{uuid4()}"
    # write some events onto stream
    await eventstoredb_client.append_to_stream(
        stream_name=stream_name,
        events=[JsonEvent(type="Junk"), JsonEvent(type="Junk")],
    )
    # write one event to get current stream-position
    marker = await eventstoredb_client.append_to_stream(
        stream_name=stream_name,
        events=[JsonEvent(type="Marker")],
    )
    assert marker.position is not None

    await eventstoredb_client.append_to_stream(
        stream_name=stream_name,
        events=[JsonEvent(type="Test")],
    )

    subscription = eventstoredb_client.subscribe_to_all(
        options=SubscribeToAllOptions(
            from_position=AllPosition(
                commit=marker.position.commit,
                prepare=marker.position.prepare,
            )
        )
    )

    subscriber.subscription = subscription

    assert subscriber.event_handler.call_count == 0

    await asyncio.sleep(0.1)
    events = [c[0][0] for c in subscriber.event_handler.call_args_list]
    events = [e for e in events if not e.event.type.startswith("$")]

    assert len(events) == 1
    assert events[0].event is not None
    event = events[0].event
    assert event.stream_name == stream_name
    assert event.type == "Test"


async def test_subscribe_to_all_exclude_system_events(
    eventstoredb_client: Client,
    subscriber: Subscriber,
) -> None:
    subscription = eventstoredb_client.subscribe_to_all(
        options=SubscribeToAllOptions(filter=ExcludeSystemEventsFilter())
    )

    subscriber.subscription = subscription

    assert subscriber.event_handler.call_count == 0

    stream_name = f"Test-{uuid4()}"
    await eventstoredb_client.append_to_stream(
        stream_name=stream_name,
        events=[JsonEvent(type="test_subscribe_to_all_exclude_system_events_Test")],
    )

    await asyncio.sleep(0.1)
    events = [c[0][0] for c in subscriber.event_handler.call_args_list]

    events = [
        e
        for e in events
        if e.event.type.startswith("$")
        or e.event.type.startswith("test_subscribe_to_all_exclude_system_events_")
    ]

    assert len(events) == 1
    assert events[0].event is not None
    event = events[0].event
    assert event.stream_name == stream_name
    assert event.type == "test_subscribe_to_all_exclude_system_events_Test"


async def test_subscribe_to_all_filter_by_event_type_regex(
    eventstoredb_client: Client,
    subscriber: Subscriber,
) -> None:
    stream_name = f"Test-{uuid4()}"
    await eventstoredb_client.append_to_stream(
        stream_name=stream_name,
        events=[
            JsonEvent(type="test_subscribe_to_all_filter_by_event_type_regex_Test1"),
            JsonEvent(type="test_subscribe_to_all_filter_by_event_type_regex_Test2"),
        ],
    )

    subscription = eventstoredb_client.subscribe_to_all(
        options=SubscribeToAllOptions(
            filter=EventTypeFilter(
                regex="test_subscribe_to_all_filter_by_event_type_regex_Test1"
            )
        )
    )

    subscriber.subscription = subscription

    await asyncio.sleep(0.1)
    events = [c[0][0] for c in subscriber.event_handler.call_args_list]

    assert len(events) == 1
    assert events[0].event is not None
    event = events[0].event
    assert event.stream_name == stream_name
    assert event.type == "test_subscribe_to_all_filter_by_event_type_regex_Test1"


async def test_subscribe_to_all_filter_by_event_type_prefix(
    eventstoredb_client: Client,
    subscriber: Subscriber,
) -> None:
    stream_name = f"Test-{uuid4()}"
    await eventstoredb_client.append_to_stream(
        stream_name=stream_name,
        events=[
            JsonEvent(type="test_subscribe_to_all_filter_by_event_type_prefix_Test1"),
            JsonEvent(type="test_subscribe_to_all_filter_by_event_type_prefix_Test2"),
            JsonEvent(type="something_else"),
        ],
    )

    subscription = eventstoredb_client.subscribe_to_all(
        options=SubscribeToAllOptions(
            filter=EventTypeFilter(
                prefix=["test_subscribe_to_all_filter_by_event_type_prefix_"]
            )
        )
    )

    subscriber.subscription = subscription

    await asyncio.sleep(0.1)
    events = [c[0][0] for c in subscriber.event_handler.call_args_list]

    assert len(events) == 2

    assert events[0].event is not None
    event = events[0].event
    assert event.stream_name == stream_name
    assert event.type == "test_subscribe_to_all_filter_by_event_type_prefix_Test1"

    assert events[1].event is not None
    event = events[1].event
    assert event.stream_name == stream_name
    assert event.type == "test_subscribe_to_all_filter_by_event_type_prefix_Test2"


async def test_subscribe_to_all_filter_by_stream_name_regex(
    eventstoredb_client: Client,
    subscriber: Subscriber,
) -> None:
    stream_name_1 = f"test_subscribe_to_all_filter_by_stream_name_regex_Test1-{uuid4()}"
    stream_name_2 = f"test_subscribe_to_all_filter_by_stream_name_regex_Test2-{uuid4()}"
    await eventstoredb_client.append_to_stream(
        stream_name=stream_name_1,
        events=[JsonEvent(type="Test")],
    )
    await eventstoredb_client.append_to_stream(
        stream_name=stream_name_2,
        events=[JsonEvent(type="Test")],
    )

    subscription = eventstoredb_client.subscribe_to_all(
        options=SubscribeToAllOptions(filter=StreamNameFilter(regex=stream_name_1))
    )

    subscriber.subscription = subscription

    await asyncio.sleep(0.1)
    events = [c[0][0] for c in subscriber.event_handler.call_args_list]

    assert len(events) == 1
    event = events[0].event
    assert event.stream_name == stream_name_1
    assert event.type == "Test"


async def test_subscribe_to_all_filter_by_stream_name_prefix(
    eventstoredb_client: Client,
    subscriber: Subscriber,
) -> None:
    stream_name_1 = (
        f"test_subscribe_to_all_filter_by_stream_name_prefix_Test1-{uuid4()}"
    )
    stream_name_2 = (
        f"test_subscribe_to_all_filter_by_stream_name_prefix_Test2-{uuid4()}"
    )
    stream_name_3 = f"Junk-{uuid4()}"
    await eventstoredb_client.append_to_stream(
        stream_name=stream_name_1,
        events=[JsonEvent(type="Test")],
    )
    await eventstoredb_client.append_to_stream(
        stream_name=stream_name_2,
        events=[JsonEvent(type="Test")],
    )
    await eventstoredb_client.append_to_stream(
        stream_name=stream_name_3,
        events=[JsonEvent(type="Test")],
    )

    subscription = eventstoredb_client.subscribe_to_all(
        options=SubscribeToAllOptions(
            filter=StreamNameFilter(
                prefix=["test_subscribe_to_all_filter_by_stream_name_prefix_"]
            )
        )
    )

    subscriber.subscription = subscription

    await asyncio.sleep(0.1)
    events = [c[0][0] for c in subscriber.event_handler.call_args_list]

    assert len(events) == 2

    event = events[0].event
    assert event.stream_name == stream_name_1
    assert event.type == "Test"

    event = events[1].event
    assert event.stream_name == stream_name_2
    assert event.type == "Test"
