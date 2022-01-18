from dataclasses import dataclass

from eventstoredb.persistent_subscriptions.common.types import (
    CreateUpdatePersistentSubscriptionOptions,
)


@dataclass
class UpdatePersistentSubscriptionOptions(CreateUpdatePersistentSubscriptionOptions):
    pass
