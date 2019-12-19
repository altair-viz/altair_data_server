from altair_data_server import Provider


def test_content_default_url():
    provider = Provider()
    try:
        content = "hello world"
        resource1 = provider.create(content=content, extension="txt")
        resource2 = provider.create(content=content, extension="txt")

        # Default URL is based on hash.
        assert resource1.url == resource2.url
        assert resource1.url.endswith(".txt")
    finally:
        provider.stop()


def test_content_route():
    provider = Provider()
    try:
        resource = provider.create(content="hello world", route="hello_world.txt")
        assert resource.url.split("/")[-1] == "hello_world.txt"
    finally:
        provider.stop()
