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
    """Backend server for Altair datasets."""

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
        self, data: pd.DataFrame, fmt: str = "json", port: Optional[int] = None
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
        return {"url": self._resources[resource_id].url}


class AltairDataServerProxied(AltairDataServer):
    """
    Backend server adaptor for use with JupyterHub.

    JupyterHub sets a JUPYTERHUB_SERVICE_PREFIX environment variable with
    the base URL of the currently running user server. This takes into account
    various factors, such as the base URL of the JupyterHub itself, named
    servers (if the user has multiple servers running), etc. Binder also
    sets the same environment variable, since it uses JupyterHub behind the
    scenes.

    jupyter-server-proxy proxies arbitrary HTTP requests sent to
    $JUPYTERHUB_SERVICE_PREFIX/proxy/<port><path> to localhost:<port><path>
    on the server.

    This transformer assumes you are running on a JupyterHub (or Binder),
    and constructs the appropriate URL for vega to reach the altair server.

    You can optionally pass in `urlpath` to override the default.
    """
    def __call__(
        self,
        data: pd.DataFrame,
        fmt: str = "json",
        port: Optional[int] = None,
        urlpath: Optional[str] = None,
    ) -> Dict[str, str]:
        result = super().__call__(data, fmt=fmt, port=port)

        url_parts = parse.urlparse(result["url"])
        if urlpath is None:
            if 'JUPYTERHUB_SERVICE_PREFIX' not in os.environ:
                raise ValueError('Not running in a JupyterHub, urlpath must be explicitly set')
            urlpath = os.environ['JUPYTERHUB_SERVICE_PREFIX']

        urlpath = urlpath.rstrip("/")

        # vega defaults to <base>/files, redirect it to <base>/proxy/<port>/<file>
        result["url"] = f"{urlpath}/proxy/{url_parts.port}{url_parts.path}"

        return result


# Singleton instances
data_server = AltairDataServer()
data_server_proxied = AltairDataServerProxied()
