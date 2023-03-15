from uuid import uuid4

import pytest

from eventstoredb import Client
from eventstoredb.events import JsonEvent
from eventstoredb.exceptions import PersistentSubscriptionAlreadyExistsError
from eventstoredb.filters import EventTypeFilter
from eventstoredb.options import (
    CreatePersistentSubscriptionToAllOptions,
    StreamPosition,
)

from .utils import EventstoreHTTP


async def test_create_persistent_subscription_to_all(
    eventstoredb_client: Client,
    eventstoredb_httpclient: EventstoreHTTP,
    group_name: str,
) -> None:
    await eventstoredb_client.create_persistent_subscription_to_all(
        group_name=group_name,
    )

    details = eventstoredb_httpclient.get_persistent_subscription_details(
        stream_name="$all",
        group_name=group_name,
    )
    assert details is not None
    assert details["eventStreamId"] == "$all"
    assert details["groupName"] == group_name


async def test_create_persistent_subscription_to_all_defaults(
    eventstoredb_client: Client,
    eventstoredb_httpclient: EventstoreHTTP,
    stream_name: str,
    group_name: str,
) -> None:
    options = CreatePersistentSubscriptionToAllOptions()
    await eventstoredb_client.create_persistent_subscription_to_all(
        group_name=group_name,
        options=options,
    )

    details = eventstoredb_httpclient.get_persistent_subscription_details(
        stream_name="$all",
        group_name=group_name,
    )
    assert details is not None
    c = details["config"]
    s = options.settings
    assert c["startFrom"] == 0
    assert c["resolveLinktos"] == s.resolve_links
    assert c["extraStatistics"] == s.extra_statistics
    assert c["maxRetryCount"] == s.max_retry_count
    assert c["checkPointAfterMilliseconds"] == s.checkpoint_after
    assert c["minCheckPointCount"] == s.min_checkpoint_count
    assert c["maxCheckPointCount"] == s.max_checkpoint_count
    assert c["maxSubscriberCount"] == s.max_subscriber_count
    assert c["liveBufferSize"] == s.live_buffer_size
    assert c["readBatchSize"] == s.read_batch_size
    assert c["bufferSize"] == s.history_buffer_size
    assert c["namedConsumerStrategy"] == "RoundRobin"


async def test_create_persistent_subscription_to_all_raises_if_exists(
    eventstoredb_client: Client,
    group_name: str,
) -> None:
    await eventstoredb_client.create_persistent_subscription_to_all(
        group_name=group_name,
    )

    with pytest.raises(PersistentSubscriptionAlreadyExistsError):
        await eventstoredb_client.create_persistent_subscription_to_all(
            group_name=group_name,
        )


async def test_create_persistent_subscription_to_all_from_start(
    eventstoredb_client: Client,
    eventstoredb_httpclient: EventstoreHTTP,
    group_name: str,
) -> None:
    await eventstoredb_client.create_persistent_subscription_to_all(
        group_name=group_name,
        options=CreatePersistentSubscriptionToAllOptions(
            from_position=StreamPosition.START
        ),
    )

    details = eventstoredb_httpclient.get_persistent_subscription_details(
        stream_name="$all",
        group_name=group_name,
    )
    assert details is not None
    assert details["config"]["startPosition"] == "C:0/P:0"


async def test_create_persistent_subscription_to_all_from_end(
    eventstoredb_client: Client,
    eventstoredb_httpclient: EventstoreHTTP,
    group_name: str,
) -> None:
    await eventstoredb_client.create_persistent_subscription_to_all(
        group_name=group_name,
        options=CreatePersistentSubscriptionToAllOptions(
            from_position=StreamPosition.END
        ),
    )

    details = eventstoredb_httpclient.get_persistent_subscription_details(
        stream_name="$all",
        group_name=group_name,
    )
    assert details is not None
    assert details["config"]["startPosition"] == "C:-1/P:-1"


async def test_create_persistent_subscription_to_all_from_position(
    eventstoredb_client: Client,
    eventstoredb_httpclient: EventstoreHTTP,
    group_name: str,
) -> None:
    marker = await eventstoredb_client.append_to_stream(
        stream_name=f"Test-{uuid4()}",
        events=JsonEvent(type="TestEvent"),
    )
    assert marker.position is not None
    await eventstoredb_client.create_persistent_subscription_to_all(
        group_name=group_name,
        options=CreatePersistentSubscriptionToAllOptions(from_position=marker.position),
    )
    details = eventstoredb_httpclient.get_persistent_subscription_details(
        stream_name="$all",
        group_name=group_name,
    )
    assert details is not None
    assert (
        details["config"]["startPosition"]
        == f"C:{marker.position.commit_position}/P:{marker.position.prepare_position}"
    )


async def test_create_persistent_subscription_to_all_filter_by_event_type_regex(
    eventstoredb_client: Client,
    eventstoredb_httpclient: EventstoreHTTP,
    group_name: str,
) -> None:
    await eventstoredb_client.create_persistent_subscription_to_all(
        group_name=group_name,
        options=CreatePersistentSubscriptionToAllOptions(
            filter=EventTypeFilter(
                regex="create_persistent_subscription_to_all_filter_by_event_type_regex"
            )
        ),
    )

    details = eventstoredb_httpclient.get_persistent_subscription_details(
        stream_name="$all",
        group_name=group_name,
    )
    assert details is not None
    # sadly we dont get the filter-settings via the http-api
