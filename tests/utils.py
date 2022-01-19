from typing import Optional
from dataclasses import dataclass
from operator import itemgetter

import requests


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
