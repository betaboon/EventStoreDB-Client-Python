from __future__ import annotations

from typing import Type, TypeVar

from grpclib.const import Status as GRPCStatus
from grpclib.exceptions import GRPCError

from eventstoredb.client.create_persistent_subscription_to_stream.exceptions import (
    PersistentSubscriptionAlreadyExistsError,
    PersistentSubscriptionDroppedError,
    PersistentSubscriptionError,
    PersistentSubscriptionMaxSubscribersReachedError,
    PersistentSubscriptionNotFoundError,
)
from eventstoredb.client.create_persistent_subscription_to_stream.types import (
    ConsumerStrategy,
    CreatePersistentSubscriptionToStreamOptions,
    PersistentSubscriptionSettings,
)
from eventstoredb.generated.event_store.client import Empty, StreamIdentifier
from eventstoredb.generated.event_store.client.persistent_subscriptions import (
    CreateReq,
    CreateReqConsumerStrategy,
    CreateReqOptions,
    CreateReqSettings,
    CreateReqStreamOptions,
    UpdateReqConsumerStrategy,
    UpdateReqSettings,
)
from eventstoredb.types import StreamPosition, StreamRevision

SettingsClass = TypeVar(
    "SettingsClass",
    CreateReqSettings,
    UpdateReqSettings,
)
ConsumerStrategyClass = TypeVar(
    "ConsumerStrategyClass",
    CreateReqConsumerStrategy,
    UpdateReqConsumerStrategy,
)


def create_persistent_subscription_request_settings(
    settings: PersistentSubscriptionSettings,
    settings_class: Type[SettingsClass],
    consumer_strategy_class: Type[ConsumerStrategyClass],
) -> SettingsClass:
    request_settings = settings_class()
    request_settings.resolve_links = settings.resolve_links
    request_settings.extra_statistics = settings.extra_statistics
    request_settings.max_retry_count = settings.max_retry_count
    request_settings.min_checkpoint_count = settings.min_checkpoint_count
    request_settings.max_checkpoint_count = settings.max_checkpoint_count
    request_settings.max_subscriber_count = settings.max_subscriber_count
    request_settings.live_buffer_size = settings.live_buffer_size
    request_settings.read_batch_size = settings.read_batch_size
    request_settings.history_buffer_size = settings.history_buffer_size
    request_settings.message_timeout_ms = settings.message_timeout
    request_settings.checkpoint_after_ms = settings.checkpoint_after

    if settings.consumer_strategy == ConsumerStrategy.DISPATCH_TO_SINGLE:
        request_settings.named_consumer_strategy = (
            consumer_strategy_class.DispatchToSingle  # type: ignore
        )
    elif settings.consumer_strategy == ConsumerStrategy.ROUND_ROBIN:
        request_settings.named_consumer_strategy = (
            consumer_strategy_class.RoundRobin  # type: ignore
        )
    elif settings.consumer_strategy == ConsumerStrategy.PINNED:
        request_settings.named_consumer_strategy = (
            consumer_strategy_class.Pinned  # type: ignore
        )

    return request_settings


def create_create_persistent_subscription_to_stream_request(
    stream_name: str,
    group_name: str,
    options: CreatePersistentSubscriptionToStreamOptions,
) -> CreateReq:
    request_options = CreateReqOptions()
    request_options.group_name = group_name

    request_options.settings = create_persistent_subscription_request_settings(
        settings=options.settings,
        settings_class=CreateReqSettings,
        consumer_strategy_class=CreateReqConsumerStrategy,
    )

    request_options.stream = CreateReqStreamOptions()
    request_options.stream.stream_identifier = StreamIdentifier(stream_name.encode())

    if isinstance(options.from_revision, StreamRevision):
        request_options.stream.revision = options.from_revision
    elif options.from_revision == StreamPosition.START:
        request_options.stream.start = Empty()
    elif options.from_revision == StreamPosition.END:
        request_options.stream.end = Empty()

    return CreateReq(options=request_options)


def convert_grpc_error_to_exception(
    error: GRPCError,
) -> PersistentSubscriptionError | GRPCError:
    if error.status == GRPCStatus.CANCELLED:
        return PersistentSubscriptionDroppedError(error.message)
    elif error.status == GRPCStatus.NOT_FOUND:
        return PersistentSubscriptionNotFoundError(error.message)
    elif error.status == GRPCStatus.ALREADY_EXISTS:
        return PersistentSubscriptionAlreadyExistsError(error.message)
    elif error.status == GRPCStatus.FAILED_PRECONDITION:
        return PersistentSubscriptionMaxSubscribersReachedError(error.message)
    else:
        return error
