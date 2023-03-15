import pytest

from eventstoredb import Client
from eventstoredb.exceptions import PersistentSubscriptionAlreadyExistsError
from eventstoredb.options import (
    CreatePersistentSubscriptionToStreamOptions,
    StreamPosition,
)

from .utils import EventstoreHTTP


async def test_create_persistent_subscription_to_stream(
    eventstoredb_client: Client,
    eventstoredb_httpclient: EventstoreHTTP,
    stream_name: str,
    group_name: str,
) -> None:
    await eventstoredb_client.create_persistent_subscription_to_stream(
        stream_name=stream_name,
        group_name=group_name,
    )

    subscriptions = eventstoredb_httpclient.get_persistent_subscriptions(
        stream_name=stream_name,
    )
    assert len(subscriptions) == 1
    s = subscriptions[0]
    assert s["eventStreamId"] == stream_name
    assert s["groupName"] == group_name


async def test_create_persistent_subscription_to_stream_defaults(
    eventstoredb_client: Client,
    eventstoredb_httpclient: EventstoreHTTP,
    stream_name: str,
    group_name: str,
) -> None:
    options = CreatePersistentSubscriptionToStreamOptions()
    await eventstoredb_client.create_persistent_subscription_to_stream(
        stream_name=stream_name,
        group_name=group_name,
        options=options,
    )

    details = eventstoredb_httpclient.get_persistent_subscription_details(
        stream_name=stream_name,
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


async def test_create_persistent_subscription_to_stream_from_start(
    eventstoredb_client: Client,
    eventstoredb_httpclient: EventstoreHTTP,
    stream_name: str,
    group_name: str,
) -> None:
    await eventstoredb_client.create_persistent_subscription_to_stream(
        stream_name=stream_name,
        group_name=group_name,
        options=CreatePersistentSubscriptionToStreamOptions(
            from_revision=StreamPosition.START
        ),
    )

    details = eventstoredb_httpclient.get_persistent_subscription_details(
        stream_name=stream_name,
        group_name=group_name,
    )
    assert details is not None
    assert details["config"]["startFrom"] == 0


async def test_create_persistent_subscription_to_stream_from_end(
    eventstoredb_client: Client,
    eventstoredb_httpclient: EventstoreHTTP,
    stream_name: str,
    group_name: str,
) -> None:
    await eventstoredb_client.create_persistent_subscription_to_stream(
        stream_name=stream_name,
        group_name=group_name,
        options=CreatePersistentSubscriptionToStreamOptions(
            from_revision=StreamPosition.END
        ),
    )

    details = eventstoredb_httpclient.get_persistent_subscription_details(
        stream_name=stream_name,
        group_name=group_name,
    )
    assert details is not None
    assert details["config"]["startFrom"] == -1


async def test_create_persistent_subscription_to_stream_from_revision(
    eventstoredb_client: Client,
    eventstoredb_httpclient: EventstoreHTTP,
    stream_name: str,
    group_name: str,
) -> None:
    await eventstoredb_client.create_persistent_subscription_to_stream(
        stream_name=stream_name,
        group_name=group_name,
        options=CreatePersistentSubscriptionToStreamOptions(from_revision=123),
    )
    details = eventstoredb_httpclient.get_persistent_subscription_details(
        stream_name=stream_name,
        group_name=group_name,
    )
    assert details is not None
    assert details["config"]["startFrom"] == 123


async def test_create_persistent_subscription_to_stream_raises_if_exists(
    eventstoredb_client: Client,
    stream_name: str,
    group_name: str,
) -> None:
    await eventstoredb_client.create_persistent_subscription_to_stream(
        stream_name=stream_name,
        group_name=group_name,
    )

    with pytest.raises(PersistentSubscriptionAlreadyExistsError):
        await eventstoredb_client.create_persistent_subscription_to_stream(
            stream_name=stream_name,
            group_name=group_name,
        )
