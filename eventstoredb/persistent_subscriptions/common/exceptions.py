class PersistentSubscriptionError(Exception):
    pass


class PersistentSubscriptionFailedError(PersistentSubscriptionError):
    pass


class PersistentSubscriptionDoesNotExistError(PersistentSubscriptionError):
    pass


class PersistentSubscriptionExistsError(PersistentSubscriptionError):
    pass


class PersistentSubscriptionDroppedError(PersistentSubscriptionError):
    pass


class PersistentSubscriptionMaxSubscribersReachedError(PersistentSubscriptionError):
    pass
