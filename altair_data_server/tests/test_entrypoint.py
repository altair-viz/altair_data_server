import altair as alt
from altair_data_server import data_server, data_server_proxied

import pytest


def test_entrypoint_exists():
    assert 'data_server' in alt.data_transformers.names()
    assert 'data_server_proxied' in alt.data_transformers.names()


@pytest.mark.parametrize('name,server_function', [
    ('data_server', data_server),
    ('data_server_proxied', data_server_proxied),
])
def test_entrypoint_identity(name, server_function):
    with alt.data_transformers.enable(name):
        transformer = alt.data_transformers.get()
    assert transformer is server_function
