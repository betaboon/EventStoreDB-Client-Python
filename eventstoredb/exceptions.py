from eventstoredb.client.append_to_stream.exceptions import (
    AppendToStreamError,
    RevisionMismatchError,
    StreamAlreadyExistsError,
)
from eventstoredb.client.create_persistent_subscription_to_stream.exceptions import (
    PersistentSubscriptionAlreadyExistsError,
    PersistentSubscriptionDroppedError,
    PersistentSubscriptionError,
    PersistentSubscriptionMaxSubscribersReachedError,
    PersistentSubscriptionNotFoundError,
)
from eventstoredb.client.exceptions import (
    ClientError,
    ConnectionStringError,
    ConnectionStringMalformedError,
    ConnectionStringMissingHostError,
    StreamNotFoundError,
)

__all__ = [
    "AppendToStreamError",
    "ClientError",
    "ConnectionStringError",
    "ConnectionStringMalformedError",
    "ConnectionStringMissingHostError",
    "PersistentSubscriptionAlreadyExistsError",
    "PersistentSubscriptionDroppedError",
    "PersistentSubscriptionError",
    "PersistentSubscriptionMaxSubscribersReachedError",
    "PersistentSubscriptionNotFoundError",
    "RevisionMismatchError",
    "StreamAlreadyExistsError",
    "StreamNotFoundError",
]
