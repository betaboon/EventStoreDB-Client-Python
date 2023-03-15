from dataclasses import dataclass

from eventstoredb.client.create_persistent_subscription_to_stream.types import (
    CreatePersistentSubscriptionToStreamOptions,
)


@dataclass
class UpdatePersistentSubscriptionToStreamOptions(
    CreatePersistentSubscriptionToStreamOptions
):
    pass
