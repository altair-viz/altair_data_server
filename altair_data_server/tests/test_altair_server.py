import re

import numpy as np
import pandas as pd
import pytest
from altair_data_server import data_server, data_server_proxied


@pytest.fixture(scope="session")
def session_context(request):
    # Reset the server at the end of the session.
    request.addfinalizer(lambda: data_server.reset())
    request.addfinalizer(lambda: data_server_proxied.reset())


@pytest.fixture
def data():
    return pd.DataFrame({
        'x': np.arange(5),
        'y': list('ABCDE')
    })


def _decode_normal_url(url, fmt):
    return url


def _decode_proxied_url(url, fmt):
    match = re.match(r'^\.\./proxy/([0-9]+)/([a-f0-9-]*\.([a-z]+))$', url)
    assert match
    assert match.group(3) == fmt

    # proxy only works when running under jupyter, use direct access here
    return 'http://localhost:{}/{}'.format(match.group(1), match.group(2))


@pytest.mark.parametrize('fmt,parse_function', [
    ('json', pd.read_json),
    ('csv', pd.read_csv),
])
@pytest.mark.parametrize('server_function,url_decoder', [
    (data_server, _decode_normal_url),
    (data_server_proxied, _decode_proxied_url),
])
def test_data_server(data, session_context, fmt, parse_function, server_function, url_decoder):
    spec = server_function(data, fmt=fmt)
    assert isinstance(spec, dict)
    assert list(spec.keys()) == ['url']

    url = url_decoder(spec['url'], fmt)
    served_data = parse_function(url)
    assert(data.equals(served_data))
