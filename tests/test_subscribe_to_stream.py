import asyncio

from eventstoredb import Client
from eventstoredb.events import JsonEvent
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

    assert len(consumer.events) == 1


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

    assert len(consumer.events) == 4

    await eventstoredb_client.append_to_stream(
        stream_name=stream_name,
        events=JsonEvent(type="Test"),
    )

    await consumer.stop(1)

    assert len(consumer.events) == 5


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

    assert len(consumer.events) == 1


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

    assert len(consumer.events) == 1

    await eventstoredb_client.append_to_stream(
        stream_name=stream_name,
        events=JsonEvent(type="Test"),
    )

    await consumer.stop(1)

    assert len(consumer.events) == 2
