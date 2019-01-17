import re

import numpy as np
import pandas as pd
import pytest
from altair_data_server import data_server


@pytest.fixture(scope="session")
def session_context(request):
    # Reset the server at the end of the session.
    request.addfinalizer(lambda: data_server.reset())


@pytest.fixture
def data():
    return pd.DataFrame({
        'x': np.arange(5),
        'y': list('ABCDE')
    })


def test_data_server_json(data, session_context):
    spec = data_server(data)
    assert isinstance(spec, dict)
    assert list(spec.keys()) == ['url']
    assert re.match('^https?://localhost:[0-9]+/[a-f0-9-]*\.json$', spec['url'])
    served_data = pd.read_json(spec['url'])
    assert(data.equals(served_data))


def test_data_server_csv(data, session_context):
    spec = data_server(data, fmt='csv')
    assert isinstance(spec, dict)
    assert list(spec.keys()) == ['url']
    assert re.match('^https?://localhost:[0-9]+/[a-f0-9-]*\.csv$', spec['url'])
    served_data = pd.read_csv(spec['url'])
    assert(data.equals(served_data))
