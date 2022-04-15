import asyncio
import logging


from eventstoredb import Client, ClientOptions

logging.basicConfig(level=logging.WARN)


async def main():
    options = ClientOptions(host="localhost", port=2113)
    client = Client(options)
    stream_name = "example-stream"
    group_name = "persistent-example"

    subscription = client.subscribe_to_persistent_subscription(
        stream_name=stream_name,
        group_name=group_name,
    )

    async for e in subscription:
        print(e)
        await subscription.ack(e)


def sync_main():
    asyncio.run(main())


if __name__ == "__main__":
    sync_main()
