from eventstoredb.client.exceptions import ClientError


class PersistentSubscriptionError(ClientError):
    pass


class PersistentSubscriptionNotFoundError(PersistentSubscriptionError):
    pass


class PersistentSubscriptionAlreadyExistsError(PersistentSubscriptionError):
    pass


class PersistentSubscriptionDroppedError(PersistentSubscriptionError):
    pass


class PersistentSubscriptionMaxSubscribersReachedError(PersistentSubscriptionError):
    pass
