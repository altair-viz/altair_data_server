# Note: the code in this file is adapted from source at
# https://github.com/googlecolab/colabtools/blob/master/google/colab/html/_background_server.py
# The following is its original license:

# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""WSGI server utilities to run in thread. WSGI chosen for easier interop."""

import threading

import portpicker
import tornado
import tornado.web
import tornado.ioloop
import tornado.httpserver
from typing import Callable, Optional, Tuple, TypeVar


def _build_server(
    started: threading.Event,
    stopped: threading.Event,
    ioloop: tornado.ioloop.IOLoop,
    app: tornado.web.Application,
    port: int,
    timeout: int,
) -> Tuple[tornado.httpserver.HTTPServer, Callable[[], None]]:
    """Closure to build the server function to be passed to the thread.

    Args:
        started: Threading event to notify when started.
        ioloop: IOLoop
        port: Port number to serve on.
        timeout: Http timeout in seconds.
        app: tornado application to serve.
    Returns:
        A function that takes a port and WSGI app and notifies
        about its status via the threading events provided.
    """


T = TypeVar("T", bound="_BackgroundServer")


class _BackgroundServer:
    """Tornado server running in a background thread."""

    _app: tornado.web.Application
    _port: Optional[int]
    _server_thread: Optional[threading.Thread]
    _ioloop: Optional[tornado.ioloop.IOLoop]
    _server: Optional[tornado.httpserver.HTTPServer]

    def __init__(self: T, app: tornado.web.Application) -> None:
        """Initialize the BackgroundServer.

        Parameters
        ----------
        app: tornado.web.Application
            application to run in the background thread.
        """
        self._app = app
        self._port = None
        self._server_thread = None
        self._ioloop = None
        self._server = None

    @property
    def app(self: T) -> tornado.web.Application:
        """Returns the app instance."""
        return self._app

    @property
    def port(self: T) -> int:
        """Returns the current port or error if the server is not started.

        Returns
        -------
        port: int
            The port being used by the server.

        Raises
        ------
        RuntimeError: If server has not been started yet.
        """
        if self._server_thread is None or self._port is None:
            raise RuntimeError("Server not running.")
        return self._port

    def stop(self: T) -> T:
        """Stops the server thread.

        If server thread is already stopped, this is a no-op.

        Returns
        -------
        self :
            Returns self for chaining.
        """
        if self._server_thread is None:
            return self
        assert self._ioloop is not None
        assert self._server is not None

        def shutdown() -> None:
            if self._server is not None:
                self._server.stop()
            if self._ioloop is not None:
                self._ioloop.stop()

        try:
            self._ioloop.add_callback(shutdown)
            self._server_thread.join()
            self._ioloop.close(all_fds=True)
        finally:
            self._server_thread = None
            self._ioloop = None
            self._server = None

        return self

    def start(
        self: T, port: Optional[int] = None, timeout: int = 1, daemon: bool = True
    ) -> T:
        """Starts a server in a thread using the provided WSGI application.

        Will wait until the thread has started to return.

        Parameters
        ----------
        port: int
            Number of the port to use for the application, will find an open
            port if one is not provided.
        timeout: int
            HTTP timeout in seconds. Default = 1.
        daemon: bool
            If True (default) use a daemon thread that will automatically terminate when
            the main process terminates.

        Returns
        -------
        self :
            Returns self for chaining.
        """
        if self._server_thread is not None:
            return self

        self._port = port

        if self._port is None:
            self._port = portpicker.pick_unused_port()

        self._ioloop = tornado.ioloop.IOLoop()
        self._server = tornado.httpserver.HTTPServer(
            self._app, idle_connection_timeout=timeout, body_timeout=timeout
        )

        def start_server(
            ioloop: tornado.ioloop.IOLoop,
            httpd: tornado.httpserver.HTTPServer,
            port: int,
        ) -> None:
            ioloop.make_current()
            httpd.listen(port=port)
            ioloop.start()

        self._server_thread = threading.Thread(
            target=start_server,
            daemon=daemon,
            kwargs={"ioloop": self._ioloop, "httpd": self._server, "port": self._port},
        )

        started = threading.Event()
        self._ioloop.add_callback(started.set)
        self._server_thread.start()
        started.wait()

        return self
