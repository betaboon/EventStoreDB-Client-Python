import pytest
import json

from eventstoredb import Client
from eventstoredb.events import JsonEvent
from eventstoredb.streams.append import (
    AppendExpectedRevision,
    AppendToStreamOptions,
    RevisionMismatchError,
    StreamExistsError,
    StreamNotFoundError,
)

from ..utils import EventstoreHTTP as HTTPClient

pytestmark = pytest.mark.asyncio


async def test_append_to_stream_one_json(
    eventstoredb_client: Client, eventstoredb_httpclient: HTTPClient, stream_name
):
    result = await eventstoredb_client.append_to_stream(
        stream_name=stream_name,
        events=JsonEvent(type="TestEvent"),
    )

    assert result.success == True
    assert result.next_expected_revision == 0

    http_events = eventstoredb_httpclient.read_stream(stream_name)
    assert len(http_events) == 1
    e = http_events[0]
    assert e["eventType"] == "TestEvent"
    assert e["eventNumber"] == 0
    assert e["isJson"] == True
    assert e["data"] == ""
    assert e["isMetaData"] == False
    assert e["metaData"] == None


async def test_append_to_stream_multiple_json(
    eventstoredb_client: Client, eventstoredb_httpclient: HTTPClient, stream_name
):
    result = await eventstoredb_client.append_to_stream(
        stream_name=stream_name,
        events=[
            JsonEvent(type="Test1"),
            JsonEvent(type="Test2"),
        ],
    )

    assert result.success == True
    assert result.next_expected_revision == 1

    http_events = eventstoredb_httpclient.read_stream(stream_name)
    assert len(http_events) == 2
    assert http_events[0]["eventType"] == "Test1"
    assert http_events[0]["eventNumber"] == 0
    assert http_events[1]["eventType"] == "Test2"
    assert http_events[1]["eventNumber"] == 1


async def test_append_to_stream_one_json_with_data(
    eventstoredb_client: Client, eventstoredb_httpclient: HTTPClient, stream_name
):
    await eventstoredb_client.append_to_stream(
        stream_name=stream_name,
        events=JsonEvent(
            type="TestEvent",
            data={"some": "data"},
        ),
    )

    http_events = eventstoredb_httpclient.read_stream(stream_name)
    assert len(http_events) == 1
    e = http_events[0]
    assert e["eventType"] == "TestEvent"
    assert e["eventNumber"] == 0
    assert e["isJson"] == True
    assert json.loads(e["data"]) == {"some": "data"}
    assert e["isMetaData"] == False
    assert e["metaData"] == None


async def test_append_to_stream_one_json_with_metadata(
    eventstoredb_client: Client, eventstoredb_httpclient: HTTPClient, stream_name
):
    await eventstoredb_client.append_to_stream(
        stream_name=stream_name,
        events=JsonEvent(
            type="TestEvent",
            metadata={"meta": "data"},
        ),
    )

    http_events = eventstoredb_httpclient.read_stream(stream_name)
    assert len(http_events) == 1
    e = http_events[0]
    assert e["eventType"] == "TestEvent"
    assert e["eventNumber"] == 0
    assert e["isJson"] == True
    assert e["data"] == ""
    assert e["isMetaData"] == True
    assert json.loads(e["metaData"]) == {"meta": "data"}


async def test_append_to_stream_one_json_with_data_and_metadata(
    eventstoredb_client: Client, eventstoredb_httpclient: HTTPClient, stream_name
):
    await eventstoredb_client.append_to_stream(
        stream_name=stream_name,
        events=JsonEvent(
            type="TestEvent",
            data={"some": "data"},
            metadata={"meta": "data"},
        ),
    )

    http_events = eventstoredb_httpclient.read_stream(stream_name)
    assert len(http_events) == 1
    assert http_events[0]["eventType"] == "TestEvent"
    assert http_events[0]["eventNumber"] == 0
    assert http_events[0]["isJson"] == True
    assert http_events[0]["isMetaData"] == True
    assert json.loads(http_events[0]["data"]) == {"some": "data"}
    assert json.loads(http_events[0]["metaData"]) == {"meta": "data"}


@pytest.mark.skip(reason="test not implemented")
async def test_append_to_stream_one_binary():
    pass


@pytest.mark.skip(reason="test not implemented")
async def test_append_to_stream_multiple_binary():
    pass


@pytest.mark.skip(reason="test not implemented")
async def test_append_to_stream_one_binary_with_data():
    pass


@pytest.mark.skip(reason="test not implemented")
async def test_append_to_stream_one_binary_with_metadata():
    pass


@pytest.mark.skip(reason="test not implemented")
async def test_append_to_stream_one_binary_with_data_and_metadata():
    pass


async def test_append_to_stream_expected_revision_any(
    eventstoredb_client: Client, eventstoredb_httpclient: HTTPClient, stream_name
):
    await eventstoredb_client.append_to_stream(
        stream_name=stream_name,
        options=AppendToStreamOptions(expected_revision=AppendExpectedRevision.ANY),
        events=JsonEvent(type="TestEvent"),
    )

    http_events = eventstoredb_httpclient.read_stream(stream_name)
    assert len(http_events) == 1
    assert http_events[0]["eventType"] == "TestEvent"


async def test_append_to_stream_expected_revision_no_stream(
    eventstoredb_client: Client, eventstoredb_httpclient: HTTPClient, stream_name
):
    await eventstoredb_client.append_to_stream(
        stream_name=stream_name,
        options=AppendToStreamOptions(
            expected_revision=AppendExpectedRevision.NO_STREAM
        ),
        events=JsonEvent(type="TestEvent"),
    )

    http_events = eventstoredb_httpclient.read_stream(stream_name)
    assert len(http_events) == 1
    assert http_events[0]["eventType"] == "TestEvent"


async def test_append_to_stream_expected_revision_no_stream_but_exists(
    eventstoredb_client: Client, stream_name
):
    await eventstoredb_client.append_to_stream(
        stream_name=stream_name,
        events=JsonEvent(type="Test1"),
    )

    with pytest.raises(StreamExistsError) as execinfo:
        await eventstoredb_client.append_to_stream(
            stream_name=stream_name,
            options=AppendToStreamOptions(
                expected_revision=AppendExpectedRevision.NO_STREAM
            ),
            events=JsonEvent(type="Test2"),
        )

    assert execinfo.value.stream_name == stream_name
    assert execinfo.value.expected_revision == AppendExpectedRevision.NO_STREAM
    assert execinfo.value.current_revision == 0


async def test_append_to_stream_expected_revision_stream_exists(
    eventstoredb_client: Client, eventstoredb_httpclient: HTTPClient, stream_name
):
    await eventstoredb_client.append_to_stream(
        stream_name=stream_name,
        events=JsonEvent(type="Test1"),
    )

    await eventstoredb_client.append_to_stream(
        stream_name=stream_name,
        options=AppendToStreamOptions(
            expected_revision=AppendExpectedRevision.STREAM_EXISTS
        ),
        events=JsonEvent(type="Test2"),
    )

    http_events = eventstoredb_httpclient.read_stream(stream_name)
    assert len(http_events) == 2
    assert http_events[0]["eventType"] == "Test1"
    assert http_events[1]["eventType"] == "Test2"


async def test_append_to_stream_expected_revision_stream_exists_but_not_exist(
    eventstoredb_client: Client, stream_name
):
    with pytest.raises(StreamNotFoundError) as execinfo:
        await eventstoredb_client.append_to_stream(
            stream_name=stream_name,
            options=AppendToStreamOptions(
                expected_revision=AppendExpectedRevision.STREAM_EXISTS
            ),
            events=JsonEvent(type="TestEvent"),
        )
    assert execinfo.value.stream_name == stream_name
    assert execinfo.value.expected_revision == AppendExpectedRevision.STREAM_EXISTS
    assert execinfo.value.current_revision == None


async def test_append_to_stream_expected_revision_exact(
    eventstoredb_client: Client, eventstoredb_httpclient: HTTPClient, stream_name
):
    await eventstoredb_client.append_to_stream(
        stream_name=stream_name,
        events=JsonEvent(type="Test1"),
    )

    await eventstoredb_client.append_to_stream(
        stream_name=stream_name,
        options=AppendToStreamOptions(expected_revision=0),
        events=JsonEvent(type="Test2"),
    )

    http_events = eventstoredb_httpclient.read_stream(stream_name)
    assert len(http_events) == 2
    assert http_events[0]["eventType"] == "Test1"
    assert http_events[1]["eventType"] == "Test2"


async def test_append_to_stream_expected_revision_exact_but_mismatch(
    eventstoredb_client: Client, stream_name
):
    await eventstoredb_client.append_to_stream(
        stream_name=stream_name,
        events=JsonEvent(type="Test1"),
    )

    with pytest.raises(RevisionMismatchError) as execinfo:
        await eventstoredb_client.append_to_stream(
            stream_name=stream_name,
            options=AppendToStreamOptions(expected_revision=1),
            events=JsonEvent(type="Test2"),
        )
    assert execinfo.value.stream_name == stream_name
    assert execinfo.value.expected_revision == 1
    assert execinfo.value.current_revision == 0


async def test_append_to_stream_expected_revision_exact_but_not_exist(
    eventstoredb_client: Client, stream_name
):
    with pytest.raises(StreamNotFoundError) as execinfo:
        await eventstoredb_client.append_to_stream(
            stream_name=stream_name,
            options=AppendToStreamOptions(expected_revision=0),
            events=JsonEvent(type="TestEvent"),
        )
    assert execinfo.value.stream_name == stream_name
    assert execinfo.value.expected_revision == 0
    assert execinfo.value.current_revision == None
