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
    subscription_before = eventstoredb_httpclient.get_persistent_subscription_details(
        stream_name=stream_name, group_name=group_name
    )
    assert subscription_before is not None

    await eventstoredb_client.delete_persistent_subscription_to_stream(
        stream_name=stream_name,
        group_name=group_name,
    )

    subscription_after = eventstoredb_httpclient.get_persistent_subscription_details(
        stream_name=stream_name,
        group_name=group_name,
    )
    assert subscription_after is None


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
