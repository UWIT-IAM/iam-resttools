"""
Contains Notify WS  DAO implementations.
"""

from resttools.mock.mock_http import MockHTTP
import re
from resttools.dao_implementation.live import get_con_pool, get_live_url
from resttools.dao_implementation.mock import get_mockdata_url

import logging
logger = logging.getLogger(__name__)


class File(object):
    """
    The File DAO implementation returns generally static content.  Use this
    DAO with this configuration:

    """
    _max_pool_size = 5

    def __init__(self, conf):
        self._conf = conf
        if 'MAX_POOL_SIZE' in conf:
            self._max_pool_size = conf['MAX_POOL_SIZE']

    def postURL(self, url, headers, body):
        logger.debug('file ntfyws post url: ' + url)

        response = get_mockdata_url("ntfyws", self._conf, url, headers)
        if response.status == 404:
            logger.debug('status 404')
            response.data = '{"error": {"code": "7000","message": "No record matched"}}'
        return response


class Live(object):
    """
    This DAO provides real data.  It requires further configuration, (conf)
    """
    _max_pool_size = 5

    def __init__(self, conf):
        self._conf = conf
        if 'MAX_POOL_SIZE' in conf:
            self._max_pool_size = conf['MAX_POOL_SIZE']

    pool = None

    def postURL(self, url, headers, body):
        if Live.pool is None:
            Live.pool = self._get_pool()

        return get_live_url(Live.pool, 'POST',
                            self._conf['HOST'],
                            url, headers=headers, body=body,
                            service_name=self._conf['SERVICE_NAME'])

    def _get_pool(self):
        return get_con_pool(self._conf['HOST'],
                            self._conf['KEY_FILE'],
                            self._conf['CERT_FILE'],
                            self._conf['CA_FILE'],
                            max_pool_size=self._max_pool_size, verify_https=False)
