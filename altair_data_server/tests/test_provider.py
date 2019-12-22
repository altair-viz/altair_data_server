import tempfile

import pytest
from tornado.httpclient import HTTPClient, HTTPClientError
import tornado.web

from altair_data_server import Provider, Resource


class RootHandler(tornado.web.RequestHandler):
    content: bytes = b"root content"

    def get(self):
        self.write(self.content)


class ProviderSubclass(Provider):
    """Test class for Provider subclassing"""

    def _handlers(self):
        handlers = super()._handlers()
        return [("/", RootHandler)] + handlers


@pytest.fixture
def http_client():
    return HTTPClient()


@pytest.fixture(scope="module")
def provider():
    provider = Provider()
    yield provider
    provider.stop()


@pytest.fixture(scope="module")
def provider_subclass():
    provider = ProviderSubclass().start()
    yield provider
    provider.stop()


def test_content_resource(provider, http_client):
    content = "testing content resource"
    resource = provider.create(content=content, extension="txt")
    assert isinstance(resource, Resource)
    assert resource.url.endswith("txt")
    assert http_client.fetch(resource.url).body.decode() == content


def test_content_default_url(provider):
    content = "testing default url"
    resource1 = provider.create(content=content, extension="txt")
    resource2 = provider.create(content=content, extension="txt")
    assert resource1.url == resource2.url


def test_content_route(provider, http_client):
    content = "testing route"
    resource = provider.create(content=content, route="hello_world.txt")
    assert resource.url.split("/")[-1] == "hello_world.txt"
    assert http_client.fetch(resource.url).body == content.encode()


def test_handler_resource(provider, http_client):
    class Handler:
        def __init__(self):
            self.count = 0

        def __call__(self):
            self.count += 1
            return f"Testing handler resource {self.count}\n"

    resource = provider.create(handler=Handler(), extension="txt")
    assert isinstance(resource, Resource)
    for i in range(1, 3):
        assert (
            http_client.fetch(resource.url).body.decode()
            == f"Testing handler resource {i}\n"
        )


def test_file_resource(provider, http_client):
    content = b"file content"
    with tempfile.NamedTemporaryFile(suffix=".txt") as f:
        f.write(content)
        f.flush()

        resource = provider.create(filepath=f.name)
        assert isinstance(resource, Resource)
        assert http_client.fetch(resource.url).body == content


def test_provider_subclass(provider_subclass, http_client):
    url = provider_subclass.url
    content = http_client.fetch(url).body
    assert content == RootHandler.content


def test_expected_404(provider, http_client):
    resource = provider.create(content="some new content")
    url = resource.url + ".html"
    with pytest.raises(HTTPClientError) as err:
        http_client.fetch(url)
    assert err.value.code == 404
