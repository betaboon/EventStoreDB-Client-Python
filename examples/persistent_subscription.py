import asyncio
import logging

from eventstoredb import Client, ClientOptions
from eventstoredb.generated.event_store.client.persistent_subscriptions import UpdateReq
from eventstoredb.persistent_subscriptions.common.exceptions import (
    PersistentSubscriptionError,
)
from eventstoredb.persistent_subscriptions.common.types import (
    PersistentSubscriptionSettings,
)
from eventstoredb.persistent_subscriptions.subscribe.subscription import (
    PersistentSubscription,
)
from eventstoredb.persistent_subscriptions.subscribe.types import NackAction
from eventstoredb.persistent_subscriptions.update.types import (
    UpdatePersistentSubscriptionOptions,
)
from tests.test_subscribe_to_stream import subscriber

logging.basicConfig(level=logging.WARN)


async def main():
    options = ClientOptions(host="localhost", port=2113)
    client = Client(options)
    stream_name = "foobar-345"
    group_name = "persistent-test"

    # await client.create_persistent_subscription(
    #     stream_name=stream_name,
    #     group_name=group_name,
    # )
    # options = UpdatePersistentSubscriptionOptions()
    # options.from_revision = 10
    # await client.update_persistent_subscription(
    #     stream_name=stream_name,
    #     group_name=group_name,
    #     options=UpdatePersistentSubscriptionOptions(
    #         settings=PersistentSubscriptionSettings(max_subscriber_count=1),
    #     ),
    # )
    subscription = client.subscribe_to_persistent_subscription(
        stream_name=stream_name,
        group_name=group_name,
    )

    try:
        async for e in subscription:
            print(e)
            await subscription.ack(e)
            # await subscription.nack(
            #     action=NackAction.PARK,
            #     reason="cos i said so",
            #     events=e,
            # )
    except PersistentSubscriptionError as e:
        print(e)
        # await subscription.ack(e)


def sync_main():
    asyncio.run(main())


if __name__ == "__main__":
    sync_main()
