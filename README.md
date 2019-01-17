# Altair data server

This package is a lightweight data transformer extension for Altair
that allows you to serve datasets from a background server.

## Usage

First install the package and its dependencies:

```
pip install git+https://github.com/altair/altair_data_server
```

Next import altair and enable the data server:
```python
import altair as alt
alt.data_transformers.enable('data_server')
```