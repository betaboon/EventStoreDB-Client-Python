import asyncio
import logging

from eventstoredb.client.client import Client
from eventstoredb.events import JsonEvent

logging.basicConfig(level=logging.WARN)


async def main() -> None:
    client = Client("esdb://localhost:2113")
    stream_name = "example-stream"
    result = await client.append_to_stream(
        stream_name=stream_name,
        events=JsonEvent(type="ExampleEvent"),
    )
    print(result)


def sync_main() -> None:
    asyncio.run(main())


if __name__ == "__main__":
    sync_main()
