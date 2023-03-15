from dataclasses import dataclass

from eventstoredb.client.create_persistent_subscription_to_all.types import (
    CreatePersistentSubscriptionToAllOptions,
)


@dataclass
class UpdatePersistentSubscriptionToAllOptions(
    CreatePersistentSubscriptionToAllOptions
):
    pass
