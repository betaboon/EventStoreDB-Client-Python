import asyncio
import logging


from eventstoredb import Client, ClientOptions

logging.basicConfig(level=logging.WARN)


async def main():
    options = ClientOptions(host="localhost", port=2113)
    client = Client(options)
    stream_name = "foobar-345"

    async for e in client.subscribe_to_stream(stream_name):
        print(e)

    # subscription = client.subscribe_to_stream(stream_name=stream_name)
    # print(subscription)
    # async for event in subscription:
    #     print(event)

    # async def subscriber():
    #     async for e in subscription:
    #         print(e)
    #
    # subscriber_task = asyncio.create_task(subscriber())
    #
    # await client.append_to_stream(stream_name, events=[JsonEvent(type="Example")])
    # await client.append_to_stream(stream_name, events=[JsonEvent(type="Example")])

    # e1 = await subscription.__anext__()
    # print(e1)
    # await client.append_to_stream(stream_name, events=[JsonEvent(type="Example")])
    # await client.append_to_stream(stream_name, events=[JsonEvent(type="Example")])
    #
    # async for event in subscription:
    #     print(event)
    # async for event in client.subscribe_to_stream(stream_name=stream_name):
    #     print(event)


def sync_main():
    asyncio.run(main())


if __name__ == "__main__":
    sync_main()
