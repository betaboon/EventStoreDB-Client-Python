import pytest
import uuid

from eventstoredb import Client
from eventstoredb.events import (
    JsonEvent,
    ReadEvent,
    RecordedEvent,
    JsonRecordedEvent,
)
from eventstoredb.streams.types import StreamPosition
from eventstoredb.streams.read import (
    ReadDirection,
    ReadStreamOptions,
    StreamNotFoundError,
)

from ..utils import json_test_events


pytestmark = pytest.mark.asyncio


def recorded_event_type(x):
    __tracebackhide__ = True
    if not isinstance(x, ReadEvent):
        pytest.fail(f"not a ReadEvent: {x}")
    if not isinstance(x.event, RecordedEvent):
        pytest.fail(f"does not contain RecordedEvent: {x}")
    else:
        return x.event.type


@pytest.mark.xfail
def test_recorded_event_type_wrong_type():
    assert recorded_event_type(None) == "Foo"


@pytest.mark.xfail
def test_recorded_event_type_no_event():
    assert recorded_event_type(ReadEvent()) == "Foo"


async def test_read_stream_json(eventstoredb_client: Client, stream_name):
    await eventstoredb_client.append_to_stream(
        stream_name=stream_name,
        events=[JsonEvent(type="Test", data={"some": "data"})],
    )

    it = eventstoredb_client.read_stream(
        stream_name=stream_name,
    )
    events = [e async for e in it]

    assert len(events) == 1
    assert isinstance(events[0], ReadEvent)
    event = events[0].event
    assert event is not None
    assert isinstance(event, RecordedEvent)
    assert event.stream_name == stream_name
    assert isinstance(event.id, uuid.UUID)
    assert event.revision == 0
    assert isinstance(event, JsonRecordedEvent)
    assert event.data is not None
    assert event.data == {"some": "data"}
    assert event.metadata == None


@pytest.mark.skip(reason="test not implemented")
async def test_read_stream_binary():
    pass


async def test_read_stream_from_start(eventstoredb_client: Client, stream_name):
    await eventstoredb_client.append_to_stream(
        stream_name=stream_name,
        events=json_test_events(4),
    )

    it = eventstoredb_client.read_stream(
        stream_name=stream_name,
        options=ReadStreamOptions(from_revision=StreamPosition.START),
    )
    events = [e async for e in it]

    assert len(events) == 4
    assert recorded_event_type(events[0]) == "Test1"
    assert recorded_event_type(events[1]) == "Test2"
    assert recorded_event_type(events[2]) == "Test3"
    assert recorded_event_type(events[3]) == "Test4"


async def test_read_stream_from_revision(eventstoredb_client: Client, stream_name):
    await eventstoredb_client.append_to_stream(
        stream_name=stream_name,
        events=json_test_events(4),
    )

    it = eventstoredb_client.read_stream(
        stream_name=stream_name,
        options=ReadStreamOptions(from_revision=2),
    )
    events = [e async for e in it]

    assert len(events) == 2
    assert recorded_event_type(events[0]) == "Test3"
    assert recorded_event_type(events[1]) == "Test4"


async def test_read_stream_backwards_from_end(eventstoredb_client: Client, stream_name):
    await eventstoredb_client.append_to_stream(
        stream_name=stream_name,
        events=json_test_events(4),
    )

    it = eventstoredb_client.read_stream(
        stream_name=stream_name,
        options=ReadStreamOptions(
            from_revision=StreamPosition.END,
            direction=ReadDirection.BACKWARDS,
        ),
    )
    events = [e async for e in it]

    assert len(events) == 4
    assert recorded_event_type(events[0]) == "Test4"
    assert recorded_event_type(events[1]) == "Test3"
    assert recorded_event_type(events[2]) == "Test2"
    assert recorded_event_type(events[3]) == "Test1"


async def test_read_stream_backwards_from_revision(
    eventstoredb_client: Client, stream_name
):
    await eventstoredb_client.append_to_stream(
        stream_name=stream_name,
        events=json_test_events(4),
    )

    it = eventstoredb_client.read_stream(
        stream_name=stream_name,
        options=ReadStreamOptions(
            from_revision=1,
            direction=ReadDirection.BACKWARDS,
        ),
    )
    events = [e async for e in it]

    assert len(events) == 2
    assert recorded_event_type(events[0]) == "Test2"
    assert recorded_event_type(events[1]) == "Test1"


async def test_read_stream_max_count(eventstoredb_client: Client, stream_name):
    await eventstoredb_client.append_to_stream(
        stream_name=stream_name,
        events=json_test_events(4),
    )

    it = eventstoredb_client.read_stream(
        stream_name=stream_name,
        options=ReadStreamOptions(max_count=2),
    )
    events = [e async for e in it]

    assert len(events) == 2
    assert recorded_event_type(events[0]) == "Test1"
    assert recorded_event_type(events[1]) == "Test2"


async def test_read_stream_max_count_from_revision(
    eventstoredb_client: Client, stream_name
):
    await eventstoredb_client.append_to_stream(
        stream_name=stream_name,
        events=json_test_events(4),
    )

    it = eventstoredb_client.read_stream(
        stream_name=stream_name,
        options=ReadStreamOptions(from_revision=1, max_count=2),
    )
    events = [e async for e in it]

    assert len(events) == 2
    assert recorded_event_type(events[0]) == "Test2"
    assert recorded_event_type(events[1]) == "Test3"


# NOTE this test currently creates a "task was destroyed"-error
# this should most likely be resolved with: https://github.com/pytest-dev/pytest-asyncio/issues/235
async def test_read_stream_stream_not_exist(eventstoredb_client: Client, stream_name):
    it = eventstoredb_client.read_stream(stream_name=stream_name)

    with pytest.raises(StreamNotFoundError) as execinfo:
        _ = [e async for e in it]

    assert execinfo.value.stream_name == stream_name


@pytest.mark.skip(reason="test not implemented")
async def test_read_stream_stream_deleted():
    pass
