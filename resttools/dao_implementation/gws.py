"""
Contains GWS DAO implementations.
"""
from resttools.mock.mock_http import MockHTTP
from resttools.dao_implementation.live import get_con_pool, get_live_url
from resttools.dao_implementation.mock import get_mockdata_url

import settings

# XXX - from production settings files
GWS_MAX_POOL_SIZE = 5


class File(object):
    """
    The File DAO implementation returns generally static content.  Use this
    DAO with this configuration:

    RESTTOOLS_GWS_DAO_CLASS = 'resttools.dao_implementation.gws.File'
    """
    def __init__(self, conf):
        self._conf = conf

    def getURL(self, url, headers):
        return get_mockdata_url("gws", "", url, headers)

    def putURL(self, url, headers, body):
        response = MockHTTP()

        if body is not None:
            if "If-Match" in headers:
                response.status = 200  # update
            else:
                response.status = 201  # create
            response.headers = {"X-Data-Source": "GWS file mock data",
                                "Content-Type": headers["Content-Type"]}
            response.data = body
        else:
            response.status = 400
            response.data = "Bad Request: no POST body"

        return response

    def deleteURL(self, url, headers):
        response = MockHTTP()
        response.status = 200
        return response


class Live(object):
    """
    This DAO provides real data.  It requires further configuration, (conf)
    """
    def __init__(self, conf):
        self._conf = conf

    pool = None

    def getURL(self, url, headers):
        if Live.pool is None:
            Live.pool = self._get_pool()

        return get_live_url(Live.pool, 'GET',
                            self._conf['GWS_HOST'],
                            url, headers=headers,
                            service_name='gws')

    def putURL(self, url, headers, body):
        if Live.pool is None:
            Live.pool = self._get_pool()

        return get_live_url(Live.pool, 'PUT',
                            self._conf['GWS_HOST'],
                            url, headers=headers, body=body,
                            service_name='gws')

    def deleteURL(self, url, headers):
        if Live.pool is None:
            Live.pool = self._get_pool()

        return get_live_url(Live.pool, 'DELETE',
                            self._conf['GWS_HOST'],
                            url, headers=headers,
                            service_name='gws')

    def _get_pool(self):
        return get_con_pool(self._conf['GWS_HOST'],
                            self._conf['GWS_KEY_FILE'],
                            self._conf['GWS_CERT_FILE'],
                            max_pool_size = GWS_MAX_POOL_SIZE)
