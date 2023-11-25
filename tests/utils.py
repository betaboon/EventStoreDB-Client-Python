from __future__ import annotations

import asyncio
from dataclasses import dataclass
from operator import itemgetter
from typing import Any, Callable, Coroutine
from urllib.parse import quote

import requests  # type: ignore

from eventstoredb.events import CaughtUp, FellBehind, JsonEvent, ReadEvent
from eventstoredb.subscriptions import PersistentSubscription, Subscription


def json_test_events(amount: int) -> list[JsonEvent]:
    events = []
    for i in range(amount):
        events.append(JsonEvent(type=f"Test{i+1}"))
    return events


@dataclass
class EventstoreHTTP:
    host: str
    port: int

    @property
    def url(self) -> str:
        return f"http://{self.host}:{self.port}"

    def read_stream(self, stream_name: str, event_id: int | None = None) -> Any:
        url = f"{self.url}/streams/{quote(stream_name)}"
        if event_id is not None:
            url = f"{url}/{event_id}"
        response = requests.get(
            url=url,
            headers={"Accept": "application/vnd.eventstore.atom+json"},
            params={"embed": "TryHarder"},
        )
        data = response.json()
        if event_id is not None:
            return data
        else:
            events = data.get("entries")
            return sorted(events, key=itemgetter("positionEventNumber"))

    def get_persistent_subscriptions(self, stream_name: str | None = None) -> Any:
        url = f"{self.url}/subscriptions"
        if stream_name:
            url = f"{url}/{stream_name}"
        response = requests.get(url=url)
        return response.json()

    def get_persistent_subscription_details(
        self, stream_name: str, group_name: str
    ) -> Any | None:
        url = f"{self.url}/subscriptions/{stream_name}/{group_name}/info"
        response = requests.get(url=url)
        if response.status_code == 200:
            return response.json()
        return None


class Consumer:
    def __init__(
        self,
        it: Subscription | PersistentSubscription,
        on_event: Callable[[Any], Coroutine[Any, Any, None]] | None = None,
    ) -> None:
        self.events: list[ReadEvent | CaughtUp | FellBehind] = []
        self._it = it
        self._on_event = on_event
        self._task: asyncio.Task[Any] | None = None
        self._consume_started = asyncio.Event()

    async def start(self) -> None:
        self._task = asyncio.create_task(self._consume())
        await self._consume_started.wait()

    async def stop(self, delay: int | float | None = None) -> None:
        if delay:
            await asyncio.sleep(delay)

        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def run_for(self, duration: int | float) -> None:
        if not self._task:
            await self.start()
        await asyncio.sleep(duration)
        await self.stop()

    async def _consume(self) -> None:
        self._consume_started.set()
        async for event in self._it:
            if self._on_event:
                await self._on_event(event)
            self.events.append(event)
