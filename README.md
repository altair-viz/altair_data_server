# Altair data server

[![build status](http://img.shields.io/travis/altair-viz/altair_data_server/master.svg?style=flat)](https://travis-ci.org/altair-viz/altair_data_server)
[![github actions](https://github.com/altair-viz/altair_data_server/workflows/build/badge.svg)](https://github.com/altair-viz/altair_data_server/actions?query=workflow%3Abuild)
[![github actions](https://github.com/altair-viz/altair_data_server/workflows/lint/badge.svg)](https://github.com/altair-viz/altair_data_server/actions?query=workflow%3Alint)
[![code style black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/altair-viz/altair_data_server/master?urlpath=lab/tree/AltairDataServer.ipynb)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/altair-viz/altair_data_server/blob/master/AltairDataServer.ipynb)


This is a data transformer plugin for [Altair](http://altair-viz.github.io)
that transparently serves data for Altair charts via a background WSGI server.

Note that charts will only render as long as your Python session is active.

The data server is a good option when you'll be **generating multiple charts as
part of an exploration of data**.

## Usage

First install the package and its dependencies:

```
$ pip install altair_data_server
```

Next import altair and enable the data server:

```python
import altair as alt
alt.data_transformers.enable('data_server')
```
Now when you create an Altair chart, the data will be served in the background
rather than embedded in the chart specification.

Once you are finished with exploration and want to generate charts that
will have their data fully embedded in the notebook, you can restore the
default data transformer:

```python
alt.data_transformers.enable('default')
```

and carry on from there.

## Remote Systems
Remotely-hosted notebooks (like JupyterHub or Binder) usually do not allow the end
user to access arbitrary ports. To enable users to work on that setup, make sure
[jupyter-server-proxy](https://github.com/jupyterhub/jupyter-server-proxy) is
installed on the jupyter server, and use the proxied data server transformer:

```python
alt.data_transformers.enable('data_server_proxied')
```

## Example

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/altair-viz/altair_data_server/master?urlpath=lab/tree/AltairDataServer.ipynb)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/altair-viz/altair_data_server/blob/master/AltairDataServer.ipynb)

You can see this in action, as well as read some of the motivation for this
plugin, in the example notebook: [AltairDataServer.ipynb](AltairDataServer.ipynb).
Click the Binder or Colab links above to try it out in your browser.

## Known Issues

Because [jupyter-server-proxy](https://github.com/jupyterhub/jupyter-server-proxy)
requires at least Python 3.5, the methods described in
[Remote Systems](#remote-systems) do not work do not work for older versions of Python.
