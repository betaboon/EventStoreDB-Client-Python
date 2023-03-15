from __future__ import annotations


class ConnectionStringError(ValueError):
    def __init__(self, connection_string: str, message: str) -> None:
        self.connection_string = connection_string
        super().__init__(message)


class ConnectionStringMalformedError(ConnectionStringError):
    def __init__(self, connection_string: str) -> None:
        super().__init__(
            connection_string=connection_string,
            message=f"ConnectionString '{connection_string}' is malformed",
        )


class ConnectionStringMissingHostError(ConnectionStringError):
    def __init__(self, connection_string: str) -> None:
        super().__init__(
            connection_string=connection_string,
            message=f"ConnectionString '{connection_string}' is missing host",
        )


class ClientException(Exception):
    ...


class StreamNotFoundError(ClientException):
    def __init__(self, stream_name: str) -> None:
        self.stream_name = stream_name
        super().__init__(f"Stream '{stream_name}' not found")
