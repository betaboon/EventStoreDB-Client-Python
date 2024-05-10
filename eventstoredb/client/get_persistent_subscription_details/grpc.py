from __future__ import annotations

from typing import TYPE_CHECKING

from eventstoredb.client.get_persistent_subscription_details.types import SubscriptionDetails
from eventstoredb.generated.event_store.client import Empty, StreamIdentifier
from eventstoredb.generated.event_store.client.persistent_subscriptions import (
    GetInfoReq,
    GetInfoReqOptions,
    GetInfoResp,
)

if TYPE_CHECKING:
    from eventstoredb.client.get_persistent_subscription_details.types import (
        GetPersistentSubscriptionDetailsOptions,
    )


def create_get_persistent_subscription_details_request(
    stream_name: str,
    group_name: str,
    options: GetPersistentSubscriptionDetailsOptions,
) -> GetInfoReq:
    request_options = GetInfoReqOptions()

    if stream_name == "$all":
        request_options.all = Empty()
    else:
        request_options.stream_identifier = StreamIdentifier(stream_name.encode())
    request_options.group_name = group_name

    return GetInfoReq(options=request_options)


def convert_get_persistent_subscription_details_response(
    response: GetInfoResp,
) -> SubscriptionDetails:
    info = response.subscription_info
    return SubscriptionDetails(
        event_source=info.event_source,
        group_name=info.group_name,
        status=info.status,
        last_known_event_position=info.last_known_event_position,
        last_checkpointed_event_position=info.last_checkpointed_event_position,
        start_from=info.start_from,
        total_in_flight_messages=info.total_in_flight_messages,
        outstanding_messages_count=info.outstanding_messages_count,
    )
