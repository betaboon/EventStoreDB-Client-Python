from eventstoredb.client.exceptions import ClientException


class PersistentSubscriptionError(ClientException):
    pass


class PersistentSubscriptionNotFoundError(PersistentSubscriptionError):
    pass


class PersistentSubscriptionAlreadyExistsError(PersistentSubscriptionError):
    pass


class PersistentSubscriptionDroppedError(PersistentSubscriptionError):
    pass


class PersistentSubscriptionMaxSubscribersReachedError(PersistentSubscriptionError):
    pass
