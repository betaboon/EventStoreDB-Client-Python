from typing import Union
from eventstoredb.streams.append.types import AppendExpectedRevision


class AppendToStreamError(Exception):
    pass


class WrongExpectedRevisionError(AppendToStreamError):
    def __init__(
        self,
        stream_name: str,
        expected_revision: Union[AppendExpectedRevision, int],
        current_revision: Union[None, int],
    ):
        self.stream_name = stream_name
        self.expected_revision = expected_revision
        self.current_revision = current_revision
        message = f"Wrong revision. expected: {self.expected_revision} got: {self.current_revision}"
        super().__init__(message)


class RevisionMismatchError(WrongExpectedRevisionError):
    pass


class StreamExistsError(WrongExpectedRevisionError):
    pass


class StreamNotFoundError(WrongExpectedRevisionError):
    pass
