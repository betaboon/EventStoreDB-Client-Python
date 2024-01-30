import typing
from uuid import uuid4

import pytest
import pytest_docker  # type: ignore
import requests
from requests.exceptions import ConnectionError

from eventstoredb import Client
from eventstoredb.options import ClientOptions

from .utils import EventstoreHTTP  # noqa: TID252


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--skip-docker-services",
        action="store_true",
        help="Skip tests that require docker-services",
    )


@pytest.fixture(autouse=True, scope="session")
def _skip_docker_services(request: pytest.FixtureRequest) -> None:
    if not request.config.option.skip_docker_services:
        return
    if "docker_services" in request.fixturenames:
        pytest.skip("skipped when not running docker-services")


def eventstoredb_is_ready(url: str) -> bool:
    try:
        response = requests.get(f"{url}/stats")
        if response.status_code == 200:
            return True
    except ConnectionError:
        pass
    return False


@pytest.fixture(scope="session")
def _eventstoredb_service(docker_services: pytest_docker.plugin.Services, docker_ip: str) -> None:
    port = docker_services.port_for("eventstore", 2113)
    url = f"http://{docker_ip}:{port}"
    docker_services.wait_until_responsive(
        timeout=30.0,
        pause=0.1,
        check=lambda: eventstoredb_is_ready(url),
    )


@pytest.fixture()
def eventstoredb_host(_eventstoredb_service: None, docker_ip: str) -> str:
    return docker_ip


@pytest.fixture()
def eventstoredb_port(
    _eventstoredb_service: None,
    docker_services: pytest_docker.plugin.Services,
) -> int:
    port = docker_services.port_for("eventstore", 2113)
    return typing.cast(int, port)


@pytest.fixture()
def eventstoredb_client(eventstoredb_host: str, eventstoredb_port: int) -> Client:
    options = ClientOptions(host=eventstoredb_host, port=eventstoredb_port)
    return Client(options=options)


@pytest.fixture()
def eventstoredb_httpclient(eventstoredb_host: str, eventstoredb_port: int) -> EventstoreHTTP:
    return EventstoreHTTP(host=eventstoredb_host, port=eventstoredb_port)


@pytest.fixture()
def stream_name() -> str:
    return f"test-stream-{uuid4()}"


@pytest.fixture()
def group_name() -> str:
    return f"test-group-{uuid4()}"
