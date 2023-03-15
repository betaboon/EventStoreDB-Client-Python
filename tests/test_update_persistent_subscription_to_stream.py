import pytest

from eventstoredb import Client
from eventstoredb.exceptions import PersistentSubscriptionNotFoundError
from eventstoredb.options import (
    CreatePersistentSubscriptionToStreamOptions,
    StreamPosition,
    UpdatePersistentSubscriptionToStreamOptions,
)

from .utils import EventstoreHTTP


async def test_update_persistent_subscription_to_stream(
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
    details_before = eventstoredb_httpclient.get_persistent_subscription_details(
        stream_name=stream_name,
        group_name=group_name,
    )
    assert details_before is not None
    assert details_before["config"]["startFrom"] == 0

    await eventstoredb_client.update_persistent_subscription_to_stream(
        stream_name=stream_name,
        group_name=group_name,
        options=UpdatePersistentSubscriptionToStreamOptions(
            from_revision=StreamPosition.END
        ),
    )

    details_after = eventstoredb_httpclient.get_persistent_subscription_details(
        stream_name=stream_name,
        group_name=group_name,
    )
    assert details_after is not None
    assert details_after["config"]["startFrom"] == -1


async def test_update_persistent_subscription_to_stream_raises_if_not_found(
    eventstoredb_client: Client,
    stream_name: str,
    group_name: str,
) -> None:
    with pytest.raises(PersistentSubscriptionNotFoundError):
        await eventstoredb_client.update_persistent_subscription_to_stream(
            stream_name=stream_name,
            group_name=group_name,
        )
