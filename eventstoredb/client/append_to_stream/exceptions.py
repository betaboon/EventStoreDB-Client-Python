from __future__ import annotations

from eventstoredb.client.append_to_stream.types import AppendExpectedRevision
from eventstoredb.client.exceptions import ClientException
from eventstoredb.types import StreamRevision


class AppendToStreamError(ClientException):
    pass


class StreamAlreadyExistsError(AppendToStreamError):
    def __init__(self, stream_name: str) -> None:
        self.stream_name = stream_name
        super().__init__(f"Stream '{stream_name}' already exists")


class RevisionMismatchError(AppendToStreamError):
    def __init__(
        self,
        stream_name: str,
        expected_revision: AppendExpectedRevision | StreamRevision,
        current_revision: StreamRevision | None,
    ) -> None:
        self.stream_name = stream_name
        self.expected_revision = expected_revision
        self.current_revision = current_revision
        message = (
            f"Stream '{stream_name}' has wrong revision. "
            f"(expected={expected_revision}, current={current_revision})"
        )
        super().__init__(message)
