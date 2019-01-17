import altair as alt
from altair_data_server import data_server


def test_entrypoint_exists():
    assert 'data_server' in alt.data_transformers.names()


def test_entrypoint_identity():
    with alt.data_transformers.enable('data_server'):
        entrypoint = alt.data_transformers.get()
    assert entrypoint is data_server