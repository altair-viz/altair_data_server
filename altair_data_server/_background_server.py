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

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import six
import socket
import threading

import portpicker
import tornado


def _build_server(started, stopped, ioloop, wsgi_app, port, timeout):
    """Closure to build the server function to be passed to the thread.

    Args:
        started: Threading event to notify when started.
        ioloop: IOLoop
        timeout: Http timeout in seconds.
        port: Port number to serve on.
        wsgi_app: WSGI application to serve.
    Returns:
        A function that function that takes a port and WSGI app and notifies
        about its status via the threading events provided.
    """
    address = ''  # Bind to all.

    # convert potential WSGI app
    if isinstance(wsgi_app, tornado.web.Application):
        app = wsgi_app
    else:
        app = tornado.wsgi.WSGIContainer(wsgi_app)

    httpd = tornado.httpserver.HTTPServer(app, idle_connection_timeout=timeout, body_timeout=timeout)

    def server():
        """Serve a WSGI application until stopped."""
        ioloop.make_current()

        httpd.listen(port=port, address=address)
        ioloop.add_callback(started.set)

        ioloop.start()

        stopped.set()

    return httpd, server


class _WsgiServer(object):
    """Wsgi server."""

    def __init__(self, wsgi_app):
        """Initialize the WsgiServer.

        Args:
        wsgi_app: WSGI pep-333 application to run.
        """
        self._app = wsgi_app
        self._server_thread = None
        # Threading.Event objects used to communicate about the status
        # of the server running in the background thread.
        # These will be initialized after building the server.
        self._stopped = None
        self._ioloop = None
        self._server = None

    @property
    def wsgi_app(self):
        """Returns the wsgi app instance."""
        return self._app

    @property
    def port(self):
        """Returns the current port or error if the server is not started.

        Raises:
        RuntimeError: If server has not been started yet.
        Returns:
        The port being used by the server.
        """
        if self._server_thread is None:
            raise RuntimeError('Server not running.')
        return self._port

    def stop(self):
        """Stops the server thread."""
        if self._server_thread is None:
            return
        self._server_thread = None

        def shutdown():
            self._server.stop()
            self._ioloop.stop()

        self._ioloop.add_callback(shutdown)
        self._stopped.wait()
        self._ioloop.close()

    def start(self, port=None, timeout=1):
        """Starts a server in a thread using the WSGI application provided.

        Will wait until the thread has started calling with an already serving
        application will simple return.

        Args:
        port: Number of the port to use for the application, will find an open
            port if one is not provided.
        timeout: Http timeout in seconds.
        """
        if self._server_thread is not None:
            return

        if port is None:
            self._port = portpicker.pick_unused_port()
        else:
            self._port = port

        started = threading.Event()
        self._stopped = threading.Event()
        self._ioloop = tornado.ioloop.IOLoop()

        wsgi_app = self.wsgi_app
        self._server, f = _build_server(started, self._stopped, self._ioloop, wsgi_app, self._port, timeout)
        server_thread = threading.Thread(target=f)
        self._server_thread = server_thread

        server_thread.start()
        started.wait()
