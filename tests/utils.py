from __future__ import annotations

import asyncio
from dataclasses import dataclass
from operator import itemgetter
from typing import Any, AsyncIterator, Awaitable, Callable, List, Optional

import requests  # type: ignore

from eventstoredb.events import JsonEvent, ReadEvent
from eventstoredb.persistent_subscriptions.subscribe import PersistentSubscription
from eventstoredb.persistent_subscriptions.subscribe.types import (
    PersistentSubscriptionEvent,
)


def json_test_events(amount: int) -> List[JsonEvent]:
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

    def read_stream(self, stream_name: str, event_id: Optional[int] = None) -> Any:
        url = f"{self.url}/streams/{stream_name}"
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

    def get_persistent_subscriptions(self, stream_name: Optional[str] = None) -> Any:
        url = f"{self.url}/subscriptions"
        if stream_name:
            url = f"{url}/{stream_name}"
        response = requests.get(url=url)
        return response.json()

    def get_persistent_subscription_details(
        self, stream_name: str, group_name: str
    ) -> Any:
        url = f"{self.url}/subscriptions/{stream_name}/{group_name}/info"
        response = requests.get(url=url)
        return response.json()


class Consumer:
    def __init__(self, it: AsyncIterator[ReadEvent]) -> None:
        self.events: list[ReadEvent] = []
        self._it = it
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
        async for e in self._it:
            self.events.append(e)


class PersistentSubscriber:
    def __init__(self, loop):
        self._loop = loop
        self._subscription: PersistentSubscription
        self.event_handler: Callable[[PersistentSubscriptionEvent], Awaitable[None]]

    @property
    def subscription(self):
        return self._subscription

    @subscription.setter
    def subscription(self, value):
        self._subscription = value
        self._task = self._loop.create_task(self._consume())

    async def _consume(self):
        async for event in self._subscription:
            await self.event_handler(event)

    async def _stop(self):
        self._task.cancel()
        try:
            await self._task
        except asyncio.CancelledError:
            pass
