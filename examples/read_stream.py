import asyncio
import logging

from eventstoredb.client.client import Client, ClientOptions
from eventstoredb.client.options import ReadStreamOptions

logging.basicConfig(level=logging.WARN)


async def main():
    options = ClientOptions(host="localhost", port=2113)
    client = Client(options)
    stream_name = "foobar-345"
    try:
        async for event in client.read_stream(stream_name=stream_name):
            print(event)
    except Exception as e:
        print(e)


def sync_main():
    asyncio.run(main())


if __name__ == "__main__":
    sync_main()
