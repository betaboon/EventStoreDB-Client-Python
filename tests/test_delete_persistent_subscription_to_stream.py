import pytest

from eventstoredb import Client
from eventstoredb.exceptions import PersistentSubscriptionNotFoundError

from .utils import EventstoreHTTP


async def test_delete_persistent_subscription_to_stream(
    eventstoredb_client: Client,
    eventstoredb_httpclient: EventstoreHTTP,
    stream_name: str,
    group_name: str,
) -> None:
    await eventstoredb_client.create_persistent_subscription_to_stream(
        stream_name=stream_name,
        group_name=group_name,
    )
    subscriptions_before = eventstoredb_httpclient.get_persistent_subscriptions(
        stream_name=stream_name,
    )
    assert len(subscriptions_before) == 1

    await eventstoredb_client.delete_persistent_subscription_to_stream(
        stream_name=stream_name,
        group_name=group_name,
    )

    subscriptions_after = eventstoredb_httpclient.get_persistent_subscriptions(
        stream_name=stream_name,
    )
    assert len(subscriptions_after) == 0


async def test_delete_persistent_subscription_to_stream_raises_if_not_found(
    eventstoredb_client: Client,
    stream_name: str,
    group_name: str,
) -> None:
    with pytest.raises(PersistentSubscriptionNotFoundError):
        await eventstoredb_client.delete_persistent_subscription_to_stream(
            stream_name=stream_name,
            group_name=group_name,
        )
