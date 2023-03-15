import pytest

from eventstoredb import Client
from eventstoredb.exceptions import PersistentSubscriptionNotFoundError

from .utils import EventstoreHTTP


async def test_delete_persistent_subscription_to_all(
    eventstoredb_client: Client,
    eventstoredb_httpclient: EventstoreHTTP,
    group_name: str,
) -> None:
    await eventstoredb_client.create_persistent_subscription_to_all(
        group_name=group_name,
    )
    subscription_before = eventstoredb_httpclient.get_persistent_subscription_details(
        stream_name="$all",
        group_name=group_name,
    )
    assert subscription_before is not None
    assert subscription_before["groupName"] == group_name

    await eventstoredb_client.delete_persistent_subscription_to_all(
        group_name=group_name,
    )

    subscription_after = eventstoredb_httpclient.get_persistent_subscription_details(
        stream_name="$all",
        group_name=group_name,
    )
    assert subscription_after is None


async def test_delete_persistent_subscription_to_all_raises_if_not_found(
    eventstoredb_client: Client,
    group_name: str,
) -> None:
    with pytest.raises(PersistentSubscriptionNotFoundError):
        await eventstoredb_client.delete_persistent_subscription_to_all(
            group_name=group_name,
        )
