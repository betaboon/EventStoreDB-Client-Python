from __future__ import annotations

from dataclasses import dataclass

from yarl import URL

from eventstoredb.client.exceptions import (
    ConnectionStringMalformedError,
    ConnectionStringMissingHostError,
)


@dataclass
class ClientOptions:
    host: str
    port: int = 2113
    username: str | None = None
    password: str | None = None
    tls: bool = True
    dns_discovery: bool = False
    keep_alive_timeout: int = 10000
    keep_alive_interval: int = 10000

    @classmethod
    def from_connection_string(cls, connection_string: str) -> ClientOptions:
        try:
            url = URL(connection_string)
        except Exception:
            raise ConnectionStringMalformedError(connection_string)

        if not url.host:
            raise ConnectionStringMissingHostError(connection_string)

        options = ClientOptions(host=url.host)

        if url.scheme == "esdb":
            options.dns_discovery = False
        elif url.scheme == "esdb+discovery":
            options.dns_discovery = True

        if url.port:
            options.port = url.port

        options.username = url.user
        options.password = url.password

        return options
