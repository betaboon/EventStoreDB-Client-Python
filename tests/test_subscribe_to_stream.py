import asyncio

from eventstoredb import Client
from eventstoredb.events import CaughtUp, JsonEvent, ReadEvent
from eventstoredb.options import StreamPosition, SubscribeToStreamOptions

from .utils import Consumer, json_test_events


async def test_subscribe_to_stream_json(
    eventstoredb_client: Client,
    stream_name: str,
) -> None:
    it = eventstoredb_client.subscribe_to_stream(stream_name=stream_name)

    consumer = Consumer(it)
    await consumer.start()

    await eventstoredb_client.append_to_stream(
        stream_name=stream_name,
        events=JsonEvent(type="Test"),
    )

    await consumer.stop(1)

    events = [e for e in consumer.events if type(e) is ReadEvent]

    assert len(events) == 1


async def test_subscribe_to_stream_from_start(
    eventstoredb_client: Client,
    stream_name: str,
) -> None:
    await eventstoredb_client.append_to_stream(
        stream_name=stream_name,
        events=json_test_events(4),
    )

    it = eventstoredb_client.subscribe_to_stream(
        stream_name=stream_name,
        options=SubscribeToStreamOptions(from_revision=StreamPosition.START),
    )

    consumer = Consumer(it)
    await consumer.start()
    await asyncio.sleep(1)

    events = [e for e in consumer.events if type(e) is ReadEvent]

    assert len(events) == 4

    await eventstoredb_client.append_to_stream(
        stream_name=stream_name,
        events=JsonEvent(type="Test"),
    )

    await consumer.stop(1)

    events = [e for e in consumer.events if type(e) is ReadEvent]

    assert len(events) == 5


async def test_subscribe_to_stream_from_end(
    eventstoredb_client: Client,
    stream_name: str,
) -> None:
    await eventstoredb_client.append_to_stream(
        stream_name=stream_name,
        events=json_test_events(4),
    )

    it = eventstoredb_client.subscribe_to_stream(
        stream_name=stream_name,
        options=SubscribeToStreamOptions(from_revision=StreamPosition.END),
    )

    consumer = Consumer(it)
    await consumer.start()

    await eventstoredb_client.append_to_stream(
        stream_name=stream_name,
        events=JsonEvent(type="Test"),
    )

    await consumer.stop(1)

    events = [e for e in consumer.events if type(e) is ReadEvent]

    assert len(events) == 1


async def test_subscribe_to_stream_from_revision(
    eventstoredb_client: Client,
    stream_name: str,
) -> None:
    await eventstoredb_client.append_to_stream(
        stream_name=stream_name,
        events=json_test_events(4),
    )

    it = eventstoredb_client.subscribe_to_stream(
        stream_name=stream_name,
        options=SubscribeToStreamOptions(from_revision=2),
    )

    consumer = Consumer(it)
    await consumer.start()
    await asyncio.sleep(1)

    events = [e for e in consumer.events if type(e) is ReadEvent]
    assert len(events) == 1

    await eventstoredb_client.append_to_stream(
        stream_name=stream_name,
        events=JsonEvent(type="Test"),
    )

    await consumer.stop(1)


async def test_caught_up_event_received(
    eventstoredb_client: Client,
    stream_name: str,
) -> None:
    await eventstoredb_client.append_to_stream(
        stream_name=stream_name,
        events=json_test_events(1),
    )

    it = eventstoredb_client.subscribe_to_stream(
        stream_name=stream_name,
        options=SubscribeToStreamOptions(from_revision=StreamPosition.START),
    )

    consumer = Consumer(it)
    await consumer.start()
    await asyncio.sleep(1)
    await consumer.stop()

    assert len(consumer.events) == 2
    assert type(consumer.events[1]) is CaughtUp
