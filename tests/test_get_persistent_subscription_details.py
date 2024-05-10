import re

from eventstoredb import Client
from eventstoredb.client.get_persistent_subscription_details.types import SubscriptionDetails


class RegexMatcher:  # noqa: PLW1641
    def __init__(self, pattern: str) -> None:
        self._regex = re.compile(pattern)

    def __eq__(self, actual: str) -> bool:  # type: ignore
        return bool(self._regex.match(actual))


async def test_get_persistent_subscription_to_all_details(
    eventstoredb_client: Client,
    group_name: str,
) -> None:
    await eventstoredb_client.create_persistent_subscription_to_all(group_name=group_name)

    details = await eventstoredb_client.get_persistent_subscription_details(
        stream_name="$all",
        group_name=group_name,
    )

    assert details == SubscriptionDetails(
        event_source="$all",
        group_name=group_name,
        status="Live",
        last_known_event_position=RegexMatcher(r"C:\d+/P:\d+"),  # type: ignore
        last_checkpointed_event_position="",
        start_from="C:0/P:0",
        total_in_flight_messages=0,
        outstanding_messages_count=0,
    )


async def test_get_persistent_subscription_to_stream_details(
    eventstoredb_client: Client,
    stream_name: str,
    group_name: str,
) -> None:
    await eventstoredb_client.create_persistent_subscription_to_stream(
        stream_name=stream_name,
        group_name=group_name,
    )

    details = await eventstoredb_client.get_persistent_subscription_details(
        stream_name=stream_name,
        group_name=group_name,
    )

    assert details == SubscriptionDetails(
        event_source=stream_name,
        group_name=group_name,
        status="Live",
        last_known_event_position="",
        last_checkpointed_event_position="",
        start_from="0",
        total_in_flight_messages=0,
        outstanding_messages_count=0,
    )
