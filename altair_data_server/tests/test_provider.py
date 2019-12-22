import tempfile
from typing import Iterator

import pytest
from tornado.httpclient import HTTPClient, HTTPClientError
import tornado.web

from altair_data_server import Provider, Resource


class RootHandler(tornado.web.RequestHandler):
    content: bytes = b"root content"

    def get(self) -> None:
        self.write(self.content)


class ProviderSubclass(Provider):
    """Test class for Provider subclassing"""

    def _handlers(self) -> list:
        handlers = super()._handlers()
        return [("/", RootHandler)] + handlers


@pytest.fixture
def http_client() -> HTTPClient:
    return HTTPClient()


@pytest.fixture(scope="module")
def provider() -> Iterator[Provider]:
    provider = Provider()
    yield provider
    provider.stop()


@pytest.fixture(scope="module")
def provider_subclass() -> Iterator[Provider]:
    provider = ProviderSubclass().start()
    yield provider
    provider.stop()


def test_content_resource(provider: Provider, http_client: HTTPClient) -> None:
    content = "testing content resource"
    resource = provider.create(content=content, extension="txt")
    assert isinstance(resource, Resource)
    assert resource.url.endswith("txt")
    assert http_client.fetch(resource.url).body.decode() == content


def test_content_default_url(provider: Provider) -> None:
    content = "testing default url"
    resource1 = provider.create(content=content, extension="txt")
    resource2 = provider.create(content=content, extension="txt")
    assert resource1.url == resource2.url


def test_content_route(provider: Provider, http_client: HTTPClient) -> None:
    content = "testing route"
    resource = provider.create(content=content, route="hello_world.txt")
    assert resource.url.split("/")[-1] == "hello_world.txt"
    assert http_client.fetch(resource.url).body == content.encode()


def test_handler_resource(provider: Provider, http_client: HTTPClient) -> None:
    class Handler:
        def __init__(self) -> None:
            self.count = 0

        def __call__(self) -> str:
            self.count += 1
            return f"Testing handler resource {self.count}\n"

    resource = provider.create(handler=Handler(), extension="txt")
    assert isinstance(resource, Resource)
    for i in range(1, 3):
        assert (
            http_client.fetch(resource.url).body.decode()
            == f"Testing handler resource {i}\n"
        )


def test_file_resource(provider: Provider, http_client: HTTPClient) -> None:
    content = b"file content"
    with tempfile.NamedTemporaryFile(suffix=".txt") as f:
        f.write(content)
        f.flush()

        resource = provider.create(filepath=f.name)
        assert isinstance(resource, Resource)
        assert http_client.fetch(resource.url).body == content


def test_provider_subclass(
    provider_subclass: Provider, http_client: HTTPClient
) -> None:
    url = provider_subclass.url
    content = http_client.fetch(url).body
    assert content == RootHandler.content


def test_expected_404(provider: Provider, http_client: HTTPClient) -> None:
    resource = provider.create(content="some new content")
    url = resource.url + ".html"
    with pytest.raises(HTTPClientError) as err:
        http_client.fetch(url)
    assert err.value.code == 404
