import asyncio

from eventstoredb import Client
from eventstoredb.options import (
    ClientOptions,
    CreatePersistentSubscriptionToStreamOptions,
)


async def main() -> None:
    options = ClientOptions(host="localhost", port=2113)
    client = Client(options)

    stream_name = "example-stream"
    group_name = "persistent-example"

    await client.create_persistent_subscription_to_stream(
        stream_name=stream_name,
        group_name=group_name,
        options=CreatePersistentSubscriptionToStreamOptions(from_revision=4),
    )


if __name__ == "__main__":
    asyncio.run(main())
