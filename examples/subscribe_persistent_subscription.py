import asyncio

from eventstoredb import Client
from eventstoredb.options import ClientOptions


async def main() -> None:
    options = ClientOptions(host="localhost", port=2113)
    client = Client(options)

    stream_name = "example-stream"
    group_name = "persistent-example"

    subscription = client.subscribe_to_persistent_subscription_to_stream(
        stream_name=stream_name,
        group_name=group_name,
    )

    async for event in subscription:
        print(event)
        await subscription.ack(event)


if __name__ == "__main__":
    asyncio.run(main())
