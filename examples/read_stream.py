import asyncio
import logging

from eventstoredb.client.client import Client, ClientOptions

logging.basicConfig(level=logging.WARN)


async def main() -> None:
    options = ClientOptions(host="localhost", port=2113)
    client = Client(options)
    stream_name = "foobar-345"
    try:
        async for event in client.read_stream(stream_name=stream_name):
            print(event)
    except Exception as e:
        print(e)


def sync_main() -> None:
    asyncio.run(main())


if __name__ == "__main__":
    sync_main()
