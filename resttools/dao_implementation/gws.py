"""
Contains GWS DAO implementations.
"""
from resttools.mock.mock_http import MockHTTP
from resttools.dao_implementation.live import get_con_pool, get_live_url
from resttools.dao_implementation.mock import get_mockdata_url


class File(object):
    """
    The File DAO implementation returns generally static content.  Use this
    DAO with this configuration:

    RESTTOOLS_GWS_DAO_CLASS = 'resttools.dao_implementation.gws.File'
    """
    _max_pool_size = 5
    _cache_db = {}

    def __init__(self, conf):
        self._conf = conf
        if 'MAX_POOL_SIZE' in conf:
            self._max_pool_size = conf['MAX_POOL_SIZE']

    def getURL(self, url, headers):
        if url not in File._cache_db:
            response = get_mockdata_url("gws", self._conf, url, headers)
        else:
            response = MockHTTP()
            response.data = File._cache_db[url]
            response.status = 200
        return response

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
    _max_pool_size = 5
    _socket_timeout = 20.0

    def __init__(self, conf):
        self._conf = conf
        if 'MAX_POOL_SIZE' in conf:
            self._max_pool_size = conf['MAX_POOL_SIZE']
        if 'SOCKET_TIMEOUT' in conf:
            self._socket_timeout = conf['SOCKET_TIMEOUT']

    pool = None

    def getURL(self, url, headers):
        if Live.pool is None:
            Live.pool = self._get_pool()

        return get_live_url(Live.pool, 'GET',
                            self._conf['HOST'],
                            url, headers=headers,
                            service_name='gws')

    def putURL(self, url, headers, body):
        if Live.pool is None:
            Live.pool = self._get_pool()

        return get_live_url(Live.pool, 'PUT',
                            self._conf['HOST'],
                            url, headers=headers, body=body,
                            service_name='gws')

    def deleteURL(self, url, headers):
        if Live.pool is None:
            Live.pool = self._get_pool()

        return get_live_url(Live.pool, 'DELETE',
                            self._conf['HOST'],
                            url, headers=headers,
                            service_name='gws')

    def _get_pool(self):
        return get_con_pool(self._conf['HOST'],
                            self._conf['KEY_FILE'],
                            self._conf['CERT_FILE'],
                            self._conf['CA_FILE'],
                            socket_timeout=self._socket_timeout,
                            max_pool_size=self._max_pool_size)
