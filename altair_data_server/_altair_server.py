"""Altair data server."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from altair_data_server._provide import _Provider


class AltairDataServer(_Provider):
    """Backend server for Altair datasets."""
    def __init__(self):
        self._altair_resources = {}
        super(AltairDataServer, self).__init__()

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
        content, resource_id = self._serialize(data, fmt)
        if resource_id not in self._altair_resources:
            self._altair_resources[resource_id] = self.create(
                content=content,
                extension=fmt,
                headers={"Access-Control-Allow-Origin": "*"}
                )
        return {'url': self._altair_resources[resource_id].url}


# Singleton instance
data_server = AltairDataServer()
