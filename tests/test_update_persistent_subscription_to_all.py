import pytest

from eventstoredb import Client
from eventstoredb.exceptions import PersistentSubscriptionNotFoundError
from eventstoredb.options import (
    CreatePersistentSubscriptionToAllOptions,
    StreamPosition,
    UpdatePersistentSubscriptionToAllOptions,
)

from .utils import EventstoreHTTP


async def test_update_persistent_subscription_to_all(
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
    details_before = eventstoredb_httpclient.get_persistent_subscription_details(
        stream_name="$all",
        group_name=group_name,
    )
    assert details_before is not None
    assert details_before["config"]["startPosition"] == "C:0/P:0"

    await eventstoredb_client.update_persistent_subscription_to_all(
        group_name=group_name,
        options=UpdatePersistentSubscriptionToAllOptions(
            from_position=StreamPosition.END
        ),
    )

    details_after = eventstoredb_httpclient.get_persistent_subscription_details(
        stream_name="$all",
        group_name=group_name,
    )
    assert details_after is not None
    assert details_after["config"]["startPosition"] == "C:-1/P:-1"


async def test_update_persistent_subscription_to_all_raises_if_not_found(
    eventstoredb_client: Client,
    group_name: str,
) -> None:
    with pytest.raises(PersistentSubscriptionNotFoundError):
        await eventstoredb_client.update_persistent_subscription_to_all(
            group_name=group_name,
        )
