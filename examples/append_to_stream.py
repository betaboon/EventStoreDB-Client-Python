import asyncio
import logging

from eventstoredb.client.client import Client, ClientOptions
from eventstoredb.events import JsonEvent

logging.basicConfig(level=logging.WARN)


async def main():
    settings = ClientOptions(host="localhost", port=2113)
    client = Client(settings)
    stream_name = "example-stream"
    result = await client.append_to_stream(
        stream_name=stream_name,
        events=JsonEvent(type="ExampleEvent"),
    )
    print(result)


def sync_main():
    asyncio.run(main())


if __name__ == "__main__":
    sync_main()
