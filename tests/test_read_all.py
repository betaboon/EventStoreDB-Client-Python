import json
from uuid import UUID, uuid4

from eventstoredb import Client
from eventstoredb.events import JsonEvent, JsonRecordedEvent, ReadEvent, RecordedEvent
from eventstoredb.filters import (
    EventTypeFilter,
    ExcludeSystemEventsFilter,
    StreamNameFilter,
)
from eventstoredb.options import ReadAllOptions, ReadDirection, StreamPosition


async def test_read_all(eventstoredb_client: Client) -> None:
    stream_name_1 = f"Test1-{uuid4()}"
    stream_name_2 = f"Test2-{uuid4()}"
    await eventstoredb_client.append_to_stream(
        stream_name=stream_name_1,
        events=[
            JsonEvent(
                type="test_read_all_Test1",
                data=json.dumps({"some": "data"}).encode(),
            )
        ],
    )
    await eventstoredb_client.append_to_stream(
        stream_name=stream_name_2,
        events=[
            JsonEvent(
                type="test_read_all_Test2",
                data=json.dumps({"some": "data"}).encode(),
            )
        ],
    )

    it = eventstoredb_client.read_all()
    # read all events and filter for events with types starting with 'test_read_all_'
    # the filtering is done because the eventstore is shared across the pytest-session
    raw_events = [e async for e in it]
    read_events = [e for e in raw_events if type(e) is ReadEvent]
    events = [
        e for e in read_events if e.event and e.event.type.startswith("test_read_all_")
    ]

    assert len(events) == 2

    assert isinstance(events[0], ReadEvent)
    event = events[0].event
    assert isinstance(event, JsonRecordedEvent)
    assert isinstance(event.id, UUID)
    assert event.stream_name == stream_name_1
    assert event.type == "test_read_all_Test1"
    assert event.revision == 0
    assert event.data == json.dumps({"some": "data"}).encode()
    assert event.metadata is None

    assert isinstance(events[1], ReadEvent)
    event = events[1].event
    assert isinstance(event, JsonRecordedEvent)
    assert isinstance(event.id, UUID)
    assert event.stream_name == stream_name_2
    assert event.type == "test_read_all_Test2"
    assert event.revision == 0
    assert event.data == json.dumps({"some": "data"}).encode()
    assert event.metadata is None


async def test_read_all_from_start(eventstoredb_client: Client) -> None:
    stream_name_1 = f"Test1-{uuid4()}"
    stream_name_2 = f"Test2-{uuid4()}"
    await eventstoredb_client.append_to_stream(
        stream_name=stream_name_1,
        events=[JsonEvent(type="test_read_all_from_start_Test1")],
    )
    await eventstoredb_client.append_to_stream(
        stream_name=stream_name_2,
        events=[JsonEvent(type="test_read_all_from_start_Test2")],
    )

    it = eventstoredb_client.read_all(
        options=ReadAllOptions(from_position=StreamPosition.START)
    )
    # read all events and filter by event-type containing the right prefix
    # the filtering is done because the eventstore is shared across the pytest-session
    raw_events = [e async for e in it]
    read_events = [e for e in raw_events if type(e) is ReadEvent]
    events = [
        e
        for e in read_events
        if e.event and e.event.type.startswith("test_read_all_from_start_")
    ]

    assert len(events) == 2

    assert isinstance(events[0], ReadEvent)
    event = events[0].event
    assert isinstance(event, RecordedEvent)
    assert event.stream_name == stream_name_1
    assert event.type == "test_read_all_from_start_Test1"

    assert isinstance(events[1], ReadEvent)
    event = events[1].event
    assert isinstance(event, RecordedEvent)
    assert event.stream_name == stream_name_2
    assert event.type == "test_read_all_from_start_Test2"


async def test_read_all_from_position(eventstoredb_client: Client) -> None:
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

    it = eventstoredb_client.read_all(
        options=ReadAllOptions(from_position=marker.position)
    )
    # read all events and filter out all system events (starting with '$')
    raw_events = [e async for e in it]
    read_events = [e for e in raw_events if type(e) is ReadEvent]
    events = [e for e in read_events if e.event and not e.event.type.startswith("$")]

    # for some odd reason read_all includes the event _at_ position
    # which seems to be different than subscribe_to_all
    assert len(events) == 2

    assert isinstance(events[0], ReadEvent)
    event = events[0].event
    assert isinstance(event, RecordedEvent)
    assert event.stream_name == stream_name
    assert event.type == "Marker"

    assert isinstance(events[1], ReadEvent)
    event = events[1].event
    assert isinstance(event, RecordedEvent)
    assert event.stream_name == stream_name
    assert event.type == "Test"


async def test_read_all_backwards_from_end(eventstoredb_client: Client) -> None:
    stream_name_1 = f"Test1-{uuid4()}"
    stream_name_2 = f"Test2-{uuid4()}"
    await eventstoredb_client.append_to_stream(
        stream_name=stream_name_1,
        events=[JsonEvent(type="test_read_all_backwards_from_end_Test1")],
    )
    await eventstoredb_client.append_to_stream(
        stream_name=stream_name_2,
        events=[JsonEvent(type="test_read_all_backwards_from_end_Test2")],
    )

    it = eventstoredb_client.read_all(
        options=ReadAllOptions(
            from_position=StreamPosition.END,
            direction=ReadDirection.BACKWARDS,
        )
    )
    # read all events and filter by event-type containing the right prefix
    # the filtering is done because the eventstore is shared across the pytest-session
    raw_events = [e async for e in it]
    read_events = [e for e in raw_events if type(e) is ReadEvent]
    events = [
        e
        for e in read_events
        if e.event and e.event.type.startswith("test_read_all_backwards_from_end_")
    ]

    assert len(events) == 2

    assert isinstance(events[0], ReadEvent)
    event = events[0].event
    assert isinstance(event, RecordedEvent)
    assert event.stream_name == stream_name_2
    assert event.type == "test_read_all_backwards_from_end_Test2"

    assert isinstance(events[1], ReadEvent)
    event = events[1].event
    assert isinstance(event, RecordedEvent)
    assert event.stream_name == stream_name_1
    assert event.type == "test_read_all_backwards_from_end_Test1"


async def test_read_all_backwards_from_position(eventstoredb_client: Client) -> None:
    stream_name = f"Test-{uuid4()}"
    # write some events onto stream
    await eventstoredb_client.append_to_stream(
        stream_name=stream_name,
        events=[JsonEvent(type="Test1"), JsonEvent(type="Test2")],
    )
    # write one event to get current stream-position
    marker = await eventstoredb_client.append_to_stream(
        stream_name=stream_name,
        events=[JsonEvent(type="Marker")],
    )
    assert marker.position is not None
    # write some events as junk
    await eventstoredb_client.append_to_stream(
        stream_name=stream_name,
        events=[JsonEvent(type="Junk"), JsonEvent(type="Junk")],
    )

    it = eventstoredb_client.read_all(
        options=ReadAllOptions(
            from_position=marker.position,
            direction=ReadDirection.BACKWARDS,
            max_count=2,
        )
    )
    # read all events and filter out all system events (starting with '$')
    raw_events = [e async for e in it]
    read_events = [e for e in raw_events if type(e) is ReadEvent]
    events = [e for e in read_events if e.event and not e.event.type.startswith("$")]
    for e in events:
        print(e)

    assert len(events) == 2

    assert isinstance(events[0], ReadEvent)
    event = events[0].event
    assert isinstance(event, RecordedEvent)
    assert event.stream_name == stream_name
    assert event.type == "Test2"

    assert isinstance(events[1], ReadEvent)
    event = events[1].event
    assert isinstance(event, RecordedEvent)
    assert event.stream_name == stream_name
    assert event.type == "Test1"


async def test_read_all_exclude_system_events(eventstoredb_client: Client) -> None:
    stream_name = f"Test-{uuid4()}"
    await eventstoredb_client.append_to_stream(
        stream_name=stream_name,
        events=[JsonEvent(type="test_read_all_exclude_system_events_Test")],
    )

    it = eventstoredb_client.read_all(
        options=ReadAllOptions(filter=ExcludeSystemEventsFilter())
    )

    raw_events = [e async for e in it]
    read_events = [e for e in raw_events if type(e) is ReadEvent]
    events = [
        e
        for e in read_events
        if e.event
        and (
            e.event.type.startswith("$")
            or e.event.type.startswith("test_read_all_exclude_system_events_")
        )
    ]

    assert len(events) == 1
    assert isinstance(events[0], ReadEvent)
    event = events[0].event
    assert isinstance(event, RecordedEvent)
    assert event.stream_name == stream_name
    assert event.type == "test_read_all_exclude_system_events_Test"


async def test_read_all_filter_by_event_type_regex(eventstoredb_client: Client) -> None:
    stream_name = f"Test-{uuid4()}"
    await eventstoredb_client.append_to_stream(
        stream_name=stream_name,
        events=[
            JsonEvent(type="test_read_all_filter_by_event_type_regex_Test1"),
            JsonEvent(type="test_read_all_filter_by_event_type_regex_Test2"),
        ],
    )

    it = eventstoredb_client.read_all(
        options=ReadAllOptions(
            filter=EventTypeFilter(
                regex="test_read_all_filter_by_event_type_regex_Test1"
            )
        )
    )

    events = [e async for e in it]

    assert len(events) == 1
    assert isinstance(events[0], ReadEvent)
    event = events[0].event
    assert isinstance(event, RecordedEvent)
    assert event.stream_name == stream_name
    assert event.type == "test_read_all_filter_by_event_type_regex_Test1"


async def test_read_all_filter_by_event_type_prefix(
    eventstoredb_client: Client,
) -> None:
    stream_name = f"Test-{uuid4()}"
    await eventstoredb_client.append_to_stream(
        stream_name=stream_name,
        events=[
            JsonEvent(type="test_read_all_filter_by_event_type_prefix_Test1"),
            JsonEvent(type="test_read_all_filter_by_event_type_prefix_Test2"),
            JsonEvent(type="something_else"),
        ],
    )

    it = eventstoredb_client.read_all(
        options=ReadAllOptions(
            filter=EventTypeFilter(
                prefix=["test_read_all_filter_by_event_type_prefix_"]
            )
        )
    )

    events = [e async for e in it]

    assert len(events) == 2
    assert isinstance(events[0], ReadEvent)
    event = events[0].event
    assert isinstance(event, RecordedEvent)
    assert event.stream_name == stream_name
    assert event.type == "test_read_all_filter_by_event_type_prefix_Test1"
    assert isinstance(events[1], ReadEvent)
    event = events[1].event
    assert isinstance(event, RecordedEvent)
    assert event.stream_name == stream_name
    assert event.type == "test_read_all_filter_by_event_type_prefix_Test2"


async def test_read_all_filter_by_stream_name_regex(
    eventstoredb_client: Client,
) -> None:
    stream_name_1 = f"Test-{uuid4()}"
    stream_name_2 = f"Test-{uuid4()}"
    await eventstoredb_client.append_to_stream(
        stream_name=stream_name_1,
        events=[JsonEvent(type="Test")],
    )
    await eventstoredb_client.append_to_stream(
        stream_name=stream_name_2,
        events=[JsonEvent(type="Test")],
    )

    it = eventstoredb_client.read_all(
        options=ReadAllOptions(filter=StreamNameFilter(regex=stream_name_1))
    )

    events = [e async for e in it]

    assert len(events) == 1
    assert isinstance(events[0], ReadEvent)
    event = events[0].event
    assert isinstance(event, RecordedEvent)
    assert event.stream_name == stream_name_1
    assert event.type == "Test"


async def test_read_all_filter_by_stream_name_prefix(
    eventstoredb_client: Client,
) -> None:
    stream_name_1 = f"FilterByStreamName1-{uuid4()}"
    stream_name_2 = f"FilterByStreamName2-{uuid4()}"
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

    it = eventstoredb_client.read_all(
        options=ReadAllOptions(filter=StreamNameFilter(prefix=["FilterByStreamName"]))
    )

    events = [e async for e in it]

    assert len(events) == 2
    assert isinstance(events[0], ReadEvent)
    event = events[0].event
    assert isinstance(event, RecordedEvent)
    assert event.stream_name == stream_name_1
    assert event.type == "Test"
    assert isinstance(events[1], ReadEvent)
    event = events[1].event
    assert isinstance(event, RecordedEvent)
    assert event.stream_name == stream_name_2
    assert event.type == "Test"
