from uuid import uuid4

from eventstoredb import Client
from eventstoredb.events import JsonEvent, ReadEvent
from eventstoredb.filters import (
    EventTypeFilter,
    ExcludeSystemEventsFilter,
    StreamNameFilter,
)
from eventstoredb.options import StreamPosition, SubscribeToAllOptions

from .utils import Consumer


async def test_subscribe_to_all(eventstoredb_client: Client) -> None:
    stream_name = f"Test-{uuid4()}"
    it = eventstoredb_client.subscribe_to_all()

    consumer = Consumer(it)
    await consumer.start()

    await eventstoredb_client.append_to_stream(
        stream_name=stream_name,
        events=[JsonEvent(type="test_subscribe_to_all_Test")],
    )

    await consumer.stop(1)

    read_events = [e for e in consumer.events if type(e) is ReadEvent]
    events = [
        e
        for e in read_events
        if e.event is not None and e.event.type.startswith("test_subscribe_to_all_")
    ]

    assert len(events) == 1
    assert events[0].event is not None
    event = events[0].event
    assert event.stream_name == stream_name
    assert event.type == "test_subscribe_to_all_Test"


async def test_subscribe_to_all_from_start(eventstoredb_client: Client) -> None:
    stream_name_1 = f"Test1-{uuid4()}"
    stream_name_2 = f"Test2-{uuid4()}"

    # append an event before subscription starts
    await eventstoredb_client.append_to_stream(
        stream_name=stream_name_1,
        events=[JsonEvent(type="test_subscribe_to_all_from_start_Test1")],
    )

    it = eventstoredb_client.subscribe_to_all(
        options=SubscribeToAllOptions(from_position=StreamPosition.START)
    )

    consumer = Consumer(it)
    await consumer.start()

    # append an event after subscription started
    await eventstoredb_client.append_to_stream(
        stream_name=stream_name_2,
        events=[JsonEvent(type="test_subscribe_to_all_from_start_Test2")],
    )

    await consumer.stop(1)

    read_events = [e for e in consumer.events if type(e) is ReadEvent]
    events = [
        e
        for e in read_events
        if e.event is not None
        and e.event.type.startswith("test_subscribe_to_all_from_start_")
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


async def test_subscribe_to_all_from_end(eventstoredb_client: Client) -> None:
    stream_name_1 = f"Test1-{uuid4()}"
    stream_name_2 = f"Test2-{uuid4()}"

    # append an event before subscription starts
    await eventstoredb_client.append_to_stream(
        stream_name=stream_name_1,
        events=[JsonEvent(type="test_subscribe_to_all_from_end_Test1")],
    )

    it = eventstoredb_client.subscribe_to_all(
        options=SubscribeToAllOptions(from_position=StreamPosition.END)
    )

    consumer = Consumer(it)
    await consumer.start()

    # append an event after subscription started
    await eventstoredb_client.append_to_stream(
        stream_name=stream_name_2,
        events=[JsonEvent(type="test_subscribe_to_all_from_end_Test2")],
    )

    await consumer.stop(1)

    read_events = [e for e in consumer.events if type(e) is ReadEvent]
    events = [
        e
        for e in read_events
        if e.event is not None
        and e.event.type.startswith("test_subscribe_to_all_from_end_")
    ]

    assert len(events) == 1
    assert events[0].event is not None
    event = events[0].event
    assert event.stream_name == stream_name_2
    assert event.type == "test_subscribe_to_all_from_end_Test2"


async def test_subscribe_to_all_from_position(eventstoredb_client: Client) -> None:
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

    it = eventstoredb_client.subscribe_to_all(
        options=SubscribeToAllOptions(from_position=marker.position)
    )

    consumer = Consumer(it)
    await consumer.run_for(1)

    read_events = [e for e in consumer.events if type(e) is ReadEvent]
    events = [
        e
        for e in read_events
        if e.event is not None and not e.event.type.startswith("$")
    ]

    assert len(events) == 1
    assert events[0].event is not None
    event = events[0].event
    assert event.stream_name == stream_name
    assert event.type == "Test"


async def test_subscribe_to_all_exclude_system_events(
    eventstoredb_client: Client,
) -> None:
    stream_name = f"Test-{uuid4()}"

    it = eventstoredb_client.subscribe_to_all(
        options=SubscribeToAllOptions(filter=ExcludeSystemEventsFilter())
    )

    consumer = Consumer(it)
    await consumer.start()

    await eventstoredb_client.append_to_stream(
        stream_name=stream_name,
        events=[JsonEvent(type="test_subscribe_to_all_exclude_system_events_Test")],
    )

    await consumer.stop(1)

    read_events = [e for e in consumer.events if type(e) is ReadEvent]
    events = [
        e
        for e in read_events
        if e.event is not None
        and (
            e.event.type.startswith("$")
            or e.event.type.startswith("test_subscribe_to_all_exclude_system_events_")
        )
    ]

    assert len(events) == 1
    assert events[0].event is not None
    event = events[0].event
    assert event.stream_name == stream_name
    assert event.type == "test_subscribe_to_all_exclude_system_events_Test"


async def test_subscribe_to_all_filter_by_event_type_regex(
    eventstoredb_client: Client,
) -> None:
    stream_name = f"Test-{uuid4()}"

    await eventstoredb_client.append_to_stream(
        stream_name=stream_name,
        events=[
            JsonEvent(type="test_subscribe_to_all_filter_by_event_type_regex_Test1"),
            JsonEvent(type="test_subscribe_to_all_filter_by_event_type_regex_Test2"),
        ],
    )

    it = eventstoredb_client.subscribe_to_all(
        options=SubscribeToAllOptions(
            filter=EventTypeFilter(
                regex="test_subscribe_to_all_filter_by_event_type_regex_Test1"
            )
        )
    )

    consumer = Consumer(it)
    await consumer.run_for(1)
    read_events = [e for e in consumer.events if type(e) is ReadEvent]
    events = [e for e in read_events]

    assert len(events) == 1
    assert events[0].event is not None
    event = events[0].event
    assert event.stream_name == stream_name
    assert event.type == "test_subscribe_to_all_filter_by_event_type_regex_Test1"


async def test_subscribe_to_all_filter_by_event_type_prefix(
    eventstoredb_client: Client,
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

    it = eventstoredb_client.subscribe_to_all(
        options=SubscribeToAllOptions(
            filter=EventTypeFilter(
                prefix=["test_subscribe_to_all_filter_by_event_type_prefix_"]
            )
        )
    )

    consumer = Consumer(it)
    await consumer.run_for(1)

    read_events = [e for e in consumer.events if type(e) is ReadEvent]
    events = [e for e in read_events]
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

    it = eventstoredb_client.subscribe_to_all(
        options=SubscribeToAllOptions(filter=StreamNameFilter(regex=stream_name_1))
    )

    consumer = Consumer(it)
    await consumer.run_for(1)

    read_events = [e for e in consumer.events if type(e) is ReadEvent]
    events = [e for e in read_events]

    assert len(events) == 1
    assert events[0].event is not None
    event = events[0].event
    assert event.stream_name == stream_name_1
    assert event.type == "Test"


async def test_subscribe_to_all_filter_by_stream_name_prefix(
    eventstoredb_client: Client,
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

    it = eventstoredb_client.subscribe_to_all(
        options=SubscribeToAllOptions(
            filter=StreamNameFilter(
                prefix=["test_subscribe_to_all_filter_by_stream_name_prefix_"]
            )
        )
    )

    consumer = Consumer(it)
    await consumer.run_for(1)

    read_events = [e for e in consumer.events if type(e) is ReadEvent]
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
