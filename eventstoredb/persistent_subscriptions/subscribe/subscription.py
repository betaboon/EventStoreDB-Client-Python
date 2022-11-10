from __future__ import annotations

import asyncio
import logging
from typing import AsyncIterator

from grpclib.exceptions import GRPCError

from eventstoredb.generated.event_store.client.persistent_subscriptions import (
    PersistentSubscriptionsStub,
    ReadReq,
)
from eventstoredb.persistent_subscriptions.common.grpc import (
    convert_grpc_error_to_exception,
)
from eventstoredb.persistent_subscriptions.subscribe.grpc import (
    convert_read_response,
    create_ack_request,
    create_nack_request,
    create_read_request,
)
from eventstoredb.persistent_subscriptions.subscribe.types import (
    NackAction,
    PersistentSubscriptionConfirmation,
    PersistentSubscriptionEvent,
    SubscribeToPersistentSubscriptionOptions,
)


class RequestQueue(AsyncIterator[ReadReq], asyncio.Queue[ReadReq]):
    def __aiter__(self) -> AsyncIterator[ReadReq]:
        return self

    async def __anext__(self) -> ReadReq:
        return await self.get()


class PersistentSubscription(AsyncIterator[PersistentSubscriptionEvent]):
    def __init__(
        self,
        client: PersistentSubscriptionsStub,
        stream_name: str,
        group_name: str,
        options: SubscribeToPersistentSubscriptionOptions | None = None,
    ) -> None:
        self.stream_name = stream_name
        self.group_name = group_name
        self._request_queue = RequestQueue()

        self._request_queue.put_nowait(
            create_read_request(
                stream_name=stream_name,
                group_name=group_name,
                options=options,
            )
        )
        self._it = client.read(self._request_queue)

    def __aiter__(self) -> AsyncIterator[PersistentSubscriptionEvent]:
        return self

    async def __anext__(self) -> PersistentSubscriptionEvent:
        while True:
            try:
                response = await self._it.__anext__()
            except GRPCError as e:
                raise convert_grpc_error_to_exception(e)
            logging.debug(f"{response=}")
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
