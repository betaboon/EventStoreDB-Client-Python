import pytest

from eventstoredb import Client
from eventstoredb.persistent_subscriptions.common.exceptions import (
    PersistentSubscriptionDoesNotExistError,
)
from eventstoredb.persistent_subscriptions.create.types import (
    CreatePersistentSubscriptionOptions,
)
from eventstoredb.streams.types import StreamPosition

from ..utils import EventstoreHTTP

pytestmark = pytest.mark.asyncio


async def test_delete_persistent_subscription(
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
    subscriptions_before = eventstoredb_httpclient.get_persistent_subscriptions(
        stream_name=stream_name,
    )
    assert len(subscriptions_before) == 1

    await eventstoredb_client.delete_persistent_subscription(
        stream_name=stream_name,
        group_name=group_name,
    )

    subscriptions_after = eventstoredb_httpclient.get_persistent_subscriptions(
        stream_name=stream_name,
    )
    assert len(subscriptions_after) == 0


async def test_delete_persistent_subscription_raises_if_not_exists(
    eventstoredb_client: Client,
    stream_name: str,
    group_name: str,
):
    with pytest.raises(PersistentSubscriptionDoesNotExistError):
        await eventstoredb_client.delete_persistent_subscription(
            stream_name=stream_name,
            group_name=group_name,
        )
