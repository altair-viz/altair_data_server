# Altair data server

[![build status](http://img.shields.io/travis/altair-viz/altair_data_server/master.svg?style=flat)](https://travis-ci.org/altair-viz/altair_data_server)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/altair-viz/altair_data_server/master?urlpath=lab/tree/AltairDataServer.ipynb)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/altair-viz/altair_data_server/blob/master/AltairDataServer.ipynb)


This is a data transformer plugin for [Altair](http://altair-viz.github.io)
that transparently serves data for Altair charts via a background WSGI server.

Note that charts will only render as long as your Python session is active.

The data server is a good option when you'll be **working locally, 
generating multiple charts as part of an exploration of data**.

**Altair data server is currently unreleased and still being tested... please
let us know if you have any feedback!**

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
will be fully embedded in the notebook, you can restore the default data transformer:
```python
alt.data_transformers.enable('default')
```
and carry on from there.

## Example

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/altair-viz/altair_data_server/blob/master/AltairDataServer.ipynb)

You can see this in action, as well as read some of the motivation for this
plugin, in the example notebook: [AltairDataServer.ipynb](AltairDataServer.ipynb).
Click the "Open in Colab" link above to run a live version of the notebook.

