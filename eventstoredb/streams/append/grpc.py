from __future__ import annotations

import betterproto

from eventstoredb.events import EventData, Position
from eventstoredb.generated.event_store.client import Empty, StreamIdentifier, Uuid
from eventstoredb.generated.event_store.client.streams import (
    AppendReq,
    AppendReqOptions,
    AppendReqProposedMessage,
    AppendResp,
    AppendRespSuccess,
    AppendRespWrongExpectedVersion,
)
from eventstoredb.streams.append.exceptions import (
    RevisionMismatchError,
    StreamExistsError,
    StreamNotFoundError,
    WrongExpectedRevisionError,
)
from eventstoredb.streams.append.types import (
    AppendExpectedRevision,
    AppendResult,
    AppendToStreamOptions,
)
from eventstoredb.streams.types import StreamRevision


def create_append_header(
    stream_name: str,
    options: AppendToStreamOptions | None = None,
) -> AppendReq:
    if options is None:
        options = AppendToStreamOptions()

    request_options = AppendReqOptions()
    request_options.stream_identifier = StreamIdentifier(stream_name.encode())

    if isinstance(options.expected_revision, StreamRevision):
        request_options.revision = options.expected_revision
    elif options.expected_revision == AppendExpectedRevision.STREAM_EXISTS:
        request_options.stream_exists = Empty()
    elif options.expected_revision == AppendExpectedRevision.NO_STREAM:
        request_options.no_stream = Empty()
    else:
        request_options.any = Empty()

    return AppendReq(options=request_options)


def create_append_request(event_data: EventData) -> AppendReq:
    message = AppendReqProposedMessage()
    message.id = Uuid(string=str(event_data.id))
    message.metadata["type"] = event_data.type
    message.metadata["content-type"] = event_data.content_type
    if event_data.data:
        message.data = event_data.data
    if event_data.metadata:
        message.custom_metadata = event_data.metadata
    return AppendReq(proposed_message=message)


def convert_append_response(stream_name: str, message: AppendResp) -> AppendResult:
    result_type, _ = betterproto.which_one_of(message, "result")
    if result_type == "wrong_expected_version":
        raise convert_wrong_expected_version(
            stream_name=stream_name,
            message=message.wrong_expected_version,
        )
    elif result_type == "success":
        return convert_append_response_success(message=message.success)
    else:
        # TODO raise a more specific exception
        raise Exception("I shouldnt be here")


def convert_append_response_success(message: AppendRespSuccess) -> AppendResult:
    position_type, _ = betterproto.which_one_of(message, "position_option")
    if position_type == "position":
        position = Position(
            commit=message.position.commit_position,
            prepare=message.position.prepare_position,
        )
    else:
        position = None
    return AppendResult(
        success=True,
        next_expected_revision=message.current_revision,
        position=position,
    )


def convert_wrong_expected_version(
    stream_name: str,
    message: AppendRespWrongExpectedVersion,
) -> WrongExpectedRevisionError:
    expected_type, _ = betterproto.which_one_of(message, "expected_revision_option")
    current_type, _ = betterproto.which_one_of(message, "current_revision_option")

    if expected_type == "expected_no_stream":
        return StreamExistsError(
            stream_name=stream_name,
            expected_revision=AppendExpectedRevision.NO_STREAM,
            current_revision=message.current_revision,
        )
    elif expected_type == "expected_stream_exists":
        return StreamNotFoundError(
            stream_name=stream_name,
            expected_revision=AppendExpectedRevision.STREAM_EXISTS,
            current_revision=None,
        )
    elif expected_type == "expected_revision" and current_type == "current_no_stream":
        return StreamNotFoundError(
            stream_name=stream_name,
            expected_revision=message.expected_revision,
            current_revision=None,
        )
    elif expected_type == "expected_revision" and current_type == "current_revision":
        return RevisionMismatchError(
            stream_name=stream_name,
            expected_revision=message.expected_revision,
            current_revision=message.current_revision,
        )
    elif expected_type == "expected_any" and current_type == "current_no_stream":
        return RevisionMismatchError(
            stream_name=stream_name,
            expected_revision=AppendExpectedRevision.ANY,
            current_revision=None,
        )
    elif expected_type == "expected_any" and current_type == "current_revision":
        return RevisionMismatchError(
            stream_name=stream_name,
            expected_revision=AppendExpectedRevision.ANY,
            current_revision=message.current_revision,
        )
    # FIXME maybe we should raise something like "UnexpectedRuntimeError" here?
    return Exception("SHOULDNT BE HERE")
