import pytest

from eventstoredb.options import ClientOptions


@pytest.mark.parametrize(
    "connection_string,client_options",
    [
        (
            "esdb://host",
            ClientOptions(
                host="host",
                port=2113,
                tls=True,
                dns_discovery=False,
            ),
        ),
        (
            "esdb://host:1234",
            ClientOptions(
                host="host",
                port=1234,
                tls=True,
                dns_discovery=False,
            ),
        ),
        (
            "esdb+discovery://host",
            ClientOptions(
                host="host",
                tls=True,
                dns_discovery=True,
            ),
        ),
        (
            "esdb://user:pass@host",
            ClientOptions(
                host="host",
                username="user",
                password="pass",
            ),
        ),
    ],
)
def test_from_url(connection_string: str, client_options: ClientOptions) -> None:
    assert ClientOptions.from_connection_string(connection_string) == client_options
