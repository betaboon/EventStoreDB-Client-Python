import asyncio
from typing import Optional, List, Callable, Awaitable
from dataclasses import dataclass
from operator import itemgetter

import requests

from eventstoredb.events import JsonEvent, ReadEvent
from eventstoredb.streams.subscribe import Subscription
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

    def read_stream(self, stream_name: str, event_id: Optional[int] = None):
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

    def get_persistent_subscriptions(self, stream_name: Optional[str] = None):
        url = f"{self.url}/subscriptions"
        if stream_name:
            url = f"{url}/{stream_name}"
        response = requests.get(url=url)
        return response.json()

    def get_persistent_subscription_details(self, stream_name: str, group_name: str):
        url = f"{self.url}/subscriptions/{stream_name}/{group_name}/info"
        response = requests.get(url=url)
        return response.json()


class Subscriber:
    def __init__(self, loop):
        self._loop = loop
        self._subscription: Subscription
        self.event_handler: Callable[[ReadEvent], None]

    @property
    def subscription(self):
        return self._subscription

    @subscription.setter
    def subscription(self, value):
        self._subscription = value
        self._task = self._loop.create_task(self._consume())

    async def _consume(self):
        async for event in self._subscription:
            self.event_handler(event)

    async def _stop(self):
        self._task.cancel()
        try:
            await self._task
        except asyncio.CancelledError:
            pass


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
