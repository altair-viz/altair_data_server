# Altair data server

[![build status](http://img.shields.io/travis/altair-viz/altair_data_server/master.svg?style=flat)](https://travis-ci.org/altair-viz/altair_data_server)

This is a data transformer plugin for [Altair](http://altair-viz.github.io)
that transparently serves data for Altair charts via a background WSGI server.

## Usage

First install the package and its dependencies:

```
$ pip install git+https://github.com/altair-viz/altair_data_server.git
```

Next import altair and enable the data server:
```python
import altair as alt
alt.data_transformers.enable('data_server')
```
Now when you create an Altair chart, the data will be served in the background
rather than embedded in the chart specification. Note that this means the
charts you create will only render as long as the Python runtime is live.

## Example

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/altair-viz/altair_data_server/blob/master/AltairDataServer.ipynb)

You can see this in action, as well as read some of the motivation for this
plugin, in the example notebook: [AltairDataServer.ipynb](AltairDataServer.ipynb).
Click the "Open in Colab" link above to run a live version of the notebook.
