from typing import TypeVar

from grpclib.const import Status as GRPCStatus
from grpclib.exceptions import GRPCError

from eventstoredb.generated.event_store.client import Empty, StreamIdentifier
from eventstoredb.generated.event_store.client.persistent_subscriptions import (
    CreateReqConsumerStrategy,
    CreateReqOptions,
    CreateReqSettings,
    CreateReqStreamOptions,
    UpdateReqConsumerStrategy,
    UpdateReqOptions,
    UpdateReqSettings,
    UpdateReqStreamOptions,
)
from eventstoredb.persistent_subscriptions.common.exceptions import (
    PersistentSubscriptionDoesNotExistError,
    PersistentSubscriptionDroppedError,
    PersistentSubscriptionError,
    PersistentSubscriptionExistsError,
    PersistentSubscriptionFailedError,
    PersistentSubscriptionMaxSubscribersReachedError,
)
from eventstoredb.persistent_subscriptions.common.types import (
    ConsumerStrategy,
    CreateUpdatePersistentSubscriptionOptions,
)
from eventstoredb.streams.types import StreamPosition, StreamRevision

Options = TypeVar("Options", CreateReqOptions, UpdateReqOptions)


def create_create_update_request_options(
    stream_name: str,
    group_name: str,
    options: CreateUpdatePersistentSubscriptionOptions,
    request_options: Options,
) -> Options:
    if isinstance(request_options, CreateReqOptions):
        request_options.stream = CreateReqStreamOptions()
        settings = CreateReqSettings()
        request_options.settings = settings
        consumer_strategy_class = CreateReqConsumerStrategy
    else:
        request_options.stream = UpdateReqStreamOptions()
        settings = UpdateReqSettings()
        request_options.settings = settings
        consumer_strategy_class = UpdateReqConsumerStrategy

    request_options.group_name = group_name
    request_options.stream.stream_identifier = StreamIdentifier(stream_name.encode())

    if isinstance(options.from_revision, StreamRevision):
        request_options.stream.revision = options.from_revision
    elif options.from_revision == StreamPosition.START:
        request_options.stream.start = Empty()
    elif options.from_revision == StreamPosition.END:
        request_options.stream.end = Empty()

    settings.resolve_links = options.settings.resolve_links
    settings.extra_statistics = options.settings.extra_statistics
    settings.max_retry_count = options.settings.max_retry_count
    settings.min_checkpoint_count = options.settings.min_checkpoint_count
    settings.max_checkpoint_count = options.settings.max_checkpoint_count
    settings.max_subscriber_count = options.settings.max_subscriber_count
    settings.live_buffer_size = options.settings.live_buffer_size
    settings.read_batch_size = options.settings.read_batch_size
    settings.history_buffer_size = options.settings.history_buffer_size
    settings.message_timeout_ms = options.settings.message_timeout
    settings.checkpoint_after_ms = options.settings.checkpoint_after

    if options.settings.consumer_strategy == ConsumerStrategy.DISPATCH_TO_SINGLE:
        settings.named_consumer_strategy = consumer_strategy_class.DispatchToSingle  # type: ignore
    elif options.settings.consumer_strategy == ConsumerStrategy.ROUND_ROBIN:
        settings.named_consumer_strategy = consumer_strategy_class.RoundRobin  # type: ignore
    elif options.settings.consumer_strategy == ConsumerStrategy.PINNED:
        settings.named_consumer_strategy = consumer_strategy_class.Pinned  # type: ignore

    return request_options


def convert_grpc_error_to_exception(error: GRPCError):
    if error.status == GRPCStatus.CANCELLED:
        return PersistentSubscriptionDroppedError(error.message)
    elif error.status == GRPCStatus.NOT_FOUND:
        return PersistentSubscriptionDoesNotExistError(error.message)
    elif error.status == GRPCStatus.ALREADY_EXISTS:
        return PersistentSubscriptionExistsError(error.message)
    elif error.status == GRPCStatus.FAILED_PRECONDITION:
        return PersistentSubscriptionMaxSubscribersReachedError(error.message)
    else:
        return error
