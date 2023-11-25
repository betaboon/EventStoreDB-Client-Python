import asyncio

from eventstoredb import Client
from eventstoredb.events import JsonEvent


async def main() -> None:
    client = Client("esdb://localhost:2113")
    stream_name = "example-stream"

    result = await client.append_to_stream(
        stream_name=stream_name,
        events=JsonEvent(type="ExampleEvent"),
    )
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
