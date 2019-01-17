# Altair data server

[![build status](http://img.shields.io/travis/altair-viz/altair_data_server/master.svg?style=flat)](https://travis-ci.org/altair-viz/altair_data_server)

This is a data transformer plugin for [Altair](http://altair-viz.github.io)
that provides data via a background WSGI server rather than embedding it in
the notebook output.

## Usage

First install the package and its dependencies:

```
pip install git+https://github.com/altair/altair_data_server.git
```

Next import altair and enable the data server:
```python
import altair as alt
alt.data_transformers.enable('data_server')
```

Now when you create an Altair chart, the data will be served in the background
rather than embedded in the chart specification. Note that this means the
chart will only render as long as the Python runtime is live.