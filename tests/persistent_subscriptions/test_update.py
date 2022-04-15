import pytest

from eventstoredb import Client
from eventstoredb.persistent_subscriptions.common.exceptions import (
    PersistentSubscriptionDoesNotExistError,
)
from eventstoredb.persistent_subscriptions.create.types import (
    CreatePersistentSubscriptionOptions,
)
from eventstoredb.persistent_subscriptions.update.types import (
    UpdatePersistentSubscriptionOptions,
)
from eventstoredb.streams.types import StreamPosition
from ..utils import EventstoreHTTP

pytestmark = pytest.mark.asyncio


async def test_update_persistent_subscription(
    eventstoredb_client: Client,
    eventstoredb_httpclient: EventstoreHTTP,
    stream_name: str,
    group_name: str,
):
    await eventstoredb_client.create_persistent_subscription(
        stream_name=stream_name,
        group_name=group_name,
        options=CreatePersistentSubscriptionOptions(from_revision=StreamPosition.START),
    )
    details_before = eventstoredb_httpclient.get_persistent_subscription_details(
        stream_name=stream_name,
        group_name=group_name,
    )
    assert details_before["config"]["startFrom"] == 0

    await eventstoredb_client.update_persistent_subscription(
        stream_name=stream_name,
        group_name=group_name,
        options=UpdatePersistentSubscriptionOptions(from_revision=StreamPosition.END),
    )

    details_after = eventstoredb_httpclient.get_persistent_subscription_details(
        stream_name=stream_name,
        group_name=group_name,
    )
    assert details_after["config"]["startFrom"] == -1


async def test_update_persistent_subscription_raises_if_not_exists(
    eventstoredb_client: Client,
    stream_name: str,
    group_name: str,
):
    with pytest.raises(PersistentSubscriptionDoesNotExistError):
        await eventstoredb_client.update_persistent_subscription(
            stream_name=stream_name,
            group_name=group_name,
        )
