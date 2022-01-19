from typing import Optional, List
from dataclasses import dataclass
from operator import itemgetter

import requests

from eventstoredb.events import JsonEvent


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
