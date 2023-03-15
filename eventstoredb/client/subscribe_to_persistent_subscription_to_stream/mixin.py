from __future__ import annotations

import asyncio
from typing import AsyncIterator

from grpclib.client import Channel
from grpclib.exceptions import GRPCError

from eventstoredb.client.create_persistent_subscription_to_stream.grpc import (
    convert_grpc_error_to_exception,
)
from eventstoredb.client.protocol import ClientProtocol
from eventstoredb.client.subscribe_to_persistent_subscription_to_stream.grpc import (
    convert_read_response,
    create_ack_request,
    create_nack_request,
    create_read_request,
)
from eventstoredb.client.subscribe_to_persistent_subscription_to_stream.types import (
    NackAction,
    PersistentSubscriptionConfirmation,
    SubscribeToPersistentSubscriptionToStreamOptions,
)
from eventstoredb.events import PersistentSubscriptionEvent
from eventstoredb.generated.event_store.client.persistent_subscriptions import (
    PersistentSubscriptionsStub,
    ReadReq,
)


class SubscribeToPersistentSubscriptionToStreamMixin(ClientProtocol):
    def subscribe_to_persistent_subscription_to_stream(
        self,
        stream_name: str,
        group_name: str,
        options: SubscribeToPersistentSubscriptionToStreamOptions | None = None,
    ) -> PersistentSubscription:
        if options is None:
            options = SubscribeToPersistentSubscriptionToStreamOptions()

        request = create_read_request(
            stream_name=stream_name,
            group_name=group_name,
            options=options,
        )

        return PersistentSubscription(
            channel=self.channel,
            read_request=request,
        )


class RequestQueue(AsyncIterator[ReadReq], asyncio.Queue[ReadReq]):
    def __aiter__(self) -> AsyncIterator[ReadReq]:
        return self

    async def __anext__(self) -> ReadReq:
        return await self.get()


class PersistentSubscription(AsyncIterator[PersistentSubscriptionEvent]):
    def __init__(
        self,
        channel: Channel,
        read_request: ReadReq,
    ) -> None:
        client = PersistentSubscriptionsStub(channel=channel)

        self._request_queue = RequestQueue()
        self._request_queue.put_nowait(read_request)
        self._it = client.read(self._request_queue)

    def __aiter__(self) -> AsyncIterator[PersistentSubscriptionEvent]:
        return self

    async def __anext__(self) -> PersistentSubscriptionEvent:
        while True:
            try:
                response = await self._it.__anext__()
            except GRPCError as e:
                raise convert_grpc_error_to_exception(e)
            event = convert_read_response(response)
            if isinstance(event, PersistentSubscriptionConfirmation):
                self.id = event.id
            else:
                return event

    async def ack(
        self,
        events: PersistentSubscriptionEvent | list[PersistentSubscriptionEvent],
    ) -> None:
        request = create_ack_request(events=events)
        await self._request_queue.put(request)

    async def nack(
        self,
        action: NackAction,
        reason: str,
        events: PersistentSubscriptionEvent | list[PersistentSubscriptionEvent],
    ) -> None:
        request = create_nack_request(action=action, reason=reason, events=events)
        await self._request_queue.put(request)
