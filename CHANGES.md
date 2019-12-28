# Altair Data Server Change Log

## Version 0.4.1

- Allow content to be served from root URL
- Fix some testing & distribution configurations

## Version 0.4.0

- Make ``Provider`` and ``Resource`` top-level imports (#21).
- Use a daemonic thread by default, so that server will automatically shut down
  when the parent python process terminates (#24).
- Facilitate subclassing of ``Provider`` class (#27).
- Add ability to specify port when enabling altair data server (#28).
- Many minor bug fixes and improvements to testing, type hints, and CI.

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