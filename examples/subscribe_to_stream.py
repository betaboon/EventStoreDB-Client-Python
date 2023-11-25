import asyncio

from eventstoredb import Client
from eventstoredb.options import ClientOptions


async def main() -> None:
    options = ClientOptions(host="localhost", port=2113)
    client = Client(options)

    stream_name = "foobar-345"

    async for event in client.subscribe_to_stream(stream_name):
        print(event)


if __name__ == "__main__":
    asyncio.run(main())
