from __future__ import annotations

from grpclib.client import Channel

from eventstoredb.client.append_to_stream.mixin import AppendToStreamMixin
from eventstoredb.client.create_persistent_subscription_to_all.mixin import (
    CreatePersistentSubscriptionToAllMixin,
)
from eventstoredb.client.create_persistent_subscription_to_stream.mixin import (
    CreatePersistentSubscriptionToStreamMixin,
)
from eventstoredb.client.delete_persistent_subscription_to_all.mixin import (
    DeletePersistentSubscriptionToAllMixin,
)
from eventstoredb.client.delete_persistent_subscription_to_stream.mixin import (
    DeletePersistentSubscriptionToStreamMixin,
)
from eventstoredb.client.read_all.mixin import ReadAllMixin
from eventstoredb.client.read_stream.mixin import ReadStreamMixin
from eventstoredb.client.subscribe_to_all.mixin import SubscribeToAllMixin
from eventstoredb.client.subscribe_to_persistent_subscription_to_all.mixin import (
    SubscribeToPersistentSubscriptionToAllMixin,
)
from eventstoredb.client.subscribe_to_persistent_subscription_to_stream.mixin import (
    SubscribeToPersistentSubscriptionToStreamMixin,
)
from eventstoredb.client.subscribe_to_stream.mixin import SubscribeToStreamMixin
from eventstoredb.client.types import ClientOptions
from eventstoredb.client.update_persistent_subscription_to_all.mixin import (
    UpdatePersistentSubscriptionToAllMixin,
)
from eventstoredb.client.update_persistent_subscription_to_stream.mixin import (
    UpdatePersistentSubscriptionToStreamMixin,
)


class Client(
    ReadStreamMixin,
    AppendToStreamMixin,
    SubscribeToStreamMixin,
    ReadAllMixin,
    SubscribeToAllMixin,
    CreatePersistentSubscriptionToStreamMixin,
    UpdatePersistentSubscriptionToStreamMixin,
    DeletePersistentSubscriptionToStreamMixin,
    SubscribeToPersistentSubscriptionToStreamMixin,
    CreatePersistentSubscriptionToAllMixin,
    UpdatePersistentSubscriptionToAllMixin,
    DeletePersistentSubscriptionToAllMixin,
    SubscribeToPersistentSubscriptionToAllMixin,
):
    def __init__(self, options: ClientOptions | str) -> None:
        if isinstance(options, str):
            self._options = ClientOptions.from_connection_string(options)
        else:
            self._options = options
        self._channel: Channel | None = None

    @property
    def channel(self) -> Channel:
        if self._channel is None:
            self._channel = Channel(host=self._options.host, port=self._options.port)
        return self._channel
