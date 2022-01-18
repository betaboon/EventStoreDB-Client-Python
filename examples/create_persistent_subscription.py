import asyncio
import logging


from eventstoredb import Client, ClientOptions
from eventstoredb.persistent_subscriptions.create.types import (
    CreatePersistentSubscriptionOptions,
)
from eventstoredb.streams.types import StreamPosition

logging.basicConfig(level=logging.WARN)


async def main():
    options = ClientOptions(host="localhost", port=2113)
    client = Client(options)
    stream_name = "example-stream"
    group_name = "persistent-example"

    await client.create_persistent_subscription(
        stream_name=stream_name,
        group_name=group_name,
        options=CreatePersistentSubscriptionOptions(from_revision=4),
    )


def sync_main():
    asyncio.run(main())


if __name__ == "__main__":
    sync_main()
