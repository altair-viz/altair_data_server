"""Altair data server."""
import os

from typing import Dict, Optional, Tuple
from urllib import parse

from altair_data_server._provide import Provider, Resource
from altair.utils.data import (
    _data_to_json_string,
    _data_to_csv_string,
    _compute_data_hash,
)
import pandas as pd


class AltairDataServer:
    """
    Backend server for Altair datasets.

    Serves datasets over HTTP dynamically so they do not need to be embedded
    in the notebook.

    By default, it starts a background server listening on an arbitrary port,
    and transforms the URLs vega uses for the datasets to fetch from the
    server. This works when the background server, the jupyter notebook and
    the user are all on the same machine - the user's local installation.

    On remote installations (like JupyterHub or Binder), the background
    server can't be directly reached by vega. Instead, the jupyter-server-proxy
    package is used to proxy user requests to the background server.
    """

    def __init__(self) -> None:
        self._provider: Optional[Provider] = None
        # We need to keep references to served resources, because the background
        # server uses weakrefs.
        self._resources: Dict[str, Resource] = {}

    def reset(self) -> None:
        if self._provider is not None:
            self._provider.stop()
        self._resources = {}

    @staticmethod
    def _serialize(data: pd.DataFrame, fmt: str) -> Tuple[str, str]:
        """Serialize data to the given format."""
        if fmt == "json":
            content = _data_to_json_string(data)
        elif fmt == "csv":
            content = _data_to_csv_string(data)
        else:
            raise ValueError(f"Unrecognized format: {fmt!r}")
        return content, _compute_data_hash(content)

    def __call__(
        self, data: pd.DataFrame, fmt: str = "json", port: Optional[int] = None, urlprefix: Optional[str] = None
    ) -> Dict[str, str]:
        if self._provider is None:
            self._provider = Provider().start(port=port)
        if port is not None and port != self._provider.port:
            self._provider.stop().start(port=port)
        content, resource_id = self._serialize(data, fmt)
        if resource_id not in self._resources:
            self._resources[resource_id] = self._provider.create(
                content=content,
                extension=fmt,
                headers={"Access-Control-Allow-Origin": "*"},
            )

        url = self._resources[resource_id].url


        # JupyterHub sets a JUPYTERHUB_SERVICE_PREFIX environment variable with
        # the base URL of the currently running user server. This takes into account
        # various factors, such as the base URL of the JupyterHub itself, named
        # servers (if the user has multiple servers running), etc. Binder also
        # sets the same environment variable, since it uses JupyterHub behind the
        # scenes.

        # jupyter-server-proxy proxies arbitrary HTTP requests sent to
        # $JUPYTERHUB_SERVICE_PREFIX/proxy/<port><path> to localhost:<port><path>
        # on the server.
        if urlprefix is None:
            if 'JUPYTERHUB_SERVICE_PREFIX' in os.environ:
                urlprefix = os.environ['JUPYTERHUB_SERVICE_PREFIX']

        if urlprefix is not None:
            url_parts = parse.urlparse(url)

            urlprefix = urlprefix.rstrip("/")

            # vega defaults to <base>/files, redirect it to <base>/proxy/<port>/<file>
            url = f'{urlprefix}/proxy/{url_parts.port}{url_parts.path}'


        return {"url": url}


class AltairDataServerProxied(AltairDataServer):
    """
    Backend server for use with JupyterHub & Binder

    Deprecated.
    """
    def __call__(
        self,
        data: pd.DataFrame,
        fmt: str = "json",
        port: Optional[int] = None,
        urlpath: Optional[str] = None,
    ) -> Dict[str, str]:
        return super().__call__(data, fmt=fmt, port=port, urlprefix=urlpath)


# Singleton instances
data_server = AltairDataServer()
data_server_proxied = AltairDataServerProxied()
