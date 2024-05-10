from __future__ import annotations

from dataclasses import dataclass


@dataclass
class GetPersistentSubscriptionDetailsOptions: ...


@dataclass
class SubscriptionDetails:
    event_source: str
    group_name: str
    status: str
    last_known_event_position: str
    last_checkpointed_event_position: str
    start_from: str
    total_in_flight_messages: int
    outstanding_messages_count: int
