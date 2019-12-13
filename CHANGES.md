# Altair Data Server Change Log

## Version 0.3.0

- Add support for Python 3.8
- Drop support for Python 3.5 and lower
- Format code with [black](https://black.readthedocs.io/)
- Add static type checking with [mypy](http://mypy-lang.org/)

## Version 0.2.1

- Add altair v4 entrypoint

## Version 0.2.0

- Add `data_server_proxied` entrypoint for use with [jupyter-server-proxy](https://github.com/jupyterhub/jupyter-server-proxy) ([#5](https://github.com/altair-viz/altair_data_server/pull/5))
- Update implementation to support Tornado 6.0 ([#6](https://github.com/altair-viz/altair_data_server/pull/6))

## Version 0.1.0

Initial release: basic Altair data server implementation with the following
entrypoints:

- ``altair.vegalite.v2.data_transformer``
- ``altair.vegalite.v3.data_transformer``