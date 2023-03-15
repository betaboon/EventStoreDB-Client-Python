from uuid import uuid4

import pytest
import requests
from requests.exceptions import ConnectionError

from eventstoredb import Client
from eventstoredb.options import ClientOptions

from .utils import EventstoreHTTP


def pytest_addoption(parser):
    parser.addoption(
        "--skip-docker-services",
        action="store_true",
        help="Skip tests that require docker-services",
    )


@pytest.fixture(autouse=True, scope="session")
def skip_docker_services(request: pytest.FixtureRequest):
    if not request.config.option.skip_docker_services:
        return
    if "docker_services" in request.fixturenames:
        pytest.skip("skipped when not running docker-services")


def eventstoredb_is_ready(url):
    try:
        response = requests.get(f"{url}/stats")
        if response.status_code == 200:
            return True
    except ConnectionError:
        return False


@pytest.fixture(scope="session")
def eventstoredb_service(docker_ip, docker_services):
    port = docker_services.port_for("eventstore.db", 2113)
    url = "http://{}:{}".format(docker_ip, port)
    docker_services.wait_until_responsive(
        timeout=30.0, pause=0.1, check=lambda: eventstoredb_is_ready(url)
    )
    return url


@pytest.fixture
def eventstoredb_host(eventstoredb_service, docker_ip):
    return docker_ip


@pytest.fixture
def eventstoredb_port(eventstoredb_service, docker_services):
    return docker_services.port_for("eventstore.db", 2113)


@pytest.fixture
def eventstoredb_client(eventstoredb_host, eventstoredb_port):
    options = ClientOptions(host=eventstoredb_host, port=eventstoredb_port)
    client = Client(options=options)
    yield client


@pytest.fixture
def eventstoredb_httpclient(eventstoredb_host, eventstoredb_port):
    client = EventstoreHTTP(host=eventstoredb_host, port=eventstoredb_port)
    yield client


@pytest.fixture
def stream_name():
    return f"test-stream-{uuid4()}"


@pytest.fixture
def group_name():
    return f"test-group-{uuid4()}"
