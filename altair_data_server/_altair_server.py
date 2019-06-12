"""Altair data server."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from six.moves.urllib.parse import urlparse

from altair_data_server._provide import _Provider


class AltairDataServer(object):
    """Backend server for Altair datasets."""
    def __init__(self):
        self._provider = None
        # We need to keep references to served resources, because the background
        # server uses weakrefs.
        self._resources = {}

    def reset(self):
        if self._provider is not None:
            self._provider.stop()
        self._resources = {}

    @staticmethod
    def _serialize(data, fmt):
        """Serialize data to the given format."""
        from altair.utils.data import _data_to_json_string, _data_to_csv_string, _compute_data_hash
        if fmt == 'json':
            content = _data_to_json_string(data)
        elif fmt == 'csv':
            content = _data_to_csv_string(data)
        else:
            raise ValueError("Unrecognized format: '{0}'".format(fmt))
        return content, _compute_data_hash(content)

    def __call__(self, data, fmt='json'):
        if self._provider is None:
            self._provider = _Provider()
        content, resource_id = self._serialize(data, fmt)
        if resource_id not in self._resources:
            self._resources[resource_id] = self._provider.create(
                content=content,
                extension=fmt,
                headers={"Access-Control-Allow-Origin": "*"}
                )
        return {'url': self._resources[resource_id].url}


class AltairDataServerProxied(AltairDataServer):
    def __call__(self, data, fmt='json'):
        result = super(AltairDataServerProxied, self).__call__(data, fmt)

        url_parts = urlparse(result['url'])
        # vega defaults to <base>/files, redirect it to <base>/proxy/<port>/<file>
        result['url'] = '../proxy/{}{}'.format(url_parts.port, url_parts.path)

        return result


# Singleton instances
data_server = AltairDataServer()
data_server_proxied = AltairDataServerProxied()
