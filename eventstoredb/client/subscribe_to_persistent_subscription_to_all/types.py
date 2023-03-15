from __future__ import annotations

from dataclasses import dataclass

from eventstoredb.client.subscribe_to_persistent_subscription_to_stream.types import (
    SubscribeToPersistentSubscriptionToStreamOptions,
)


@dataclass
class SubscribeToPersistentSubscriptionToAllOptions(
    SubscribeToPersistentSubscriptionToStreamOptions
):
    ...
