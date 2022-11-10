from __future__ import annotations

from eventstoredb.streams.append.types import AppendExpectedRevision


class AppendToStreamError(Exception):
    pass


class WrongExpectedRevisionError(AppendToStreamError):
    def __init__(
        self,
        stream_name: str,
        expected_revision: int | AppendExpectedRevision,
        current_revision: int | None,
    ):
        self.stream_name = stream_name
        self.expected_revision = expected_revision
        self.current_revision = current_revision
        message = (
            f"Wrong revision. "
            f"expected: {self.expected_revision} "
            f"got: {self.current_revision}"
        )
        super().__init__(message)


class RevisionMismatchError(WrongExpectedRevisionError):
    pass


class StreamExistsError(WrongExpectedRevisionError):
    pass


class StreamNotFoundError(WrongExpectedRevisionError):
    pass
