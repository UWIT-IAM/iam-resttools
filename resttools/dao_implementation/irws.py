"""
Contains IRWS DAO implementations.
"""

from resttools.mock.mock_http import MockHTTP
import re
from resttools.dao_implementation.live import get_con_pool, get_live_url
from resttools.dao_implementation.mock import get_mockdata_url

import logging
logger = logging.getLogger(__name__)

IRWS_MAX_POOL_SIZE = 10

class File(object):
    """
    The File DAO implementation returns generally static content.  Use this
    DAO with this configuration:

    """
    def __init__(self, conf):
        self._conf = conf

    def getURL(self, url, headers):
        logger.debug('file irws get url: ' + url)
        response = get_mockdata_url("irws", "", url, headers)
        if response.status==404:
            logger.debug('status 404')
            response.data = '{"error": {"code": "7000","message": "No record matched"}}'
        return response

    def putURL(self, url, headers, body):
        logger.debug('file irws put url: ' + url)

        response = get_mockdata_url("irws", "", url, headers)
        if response.status==404:
            logger.debug('status 404')
            response.data = '{"error": {"code": "7000","message": "No record matched"}}'
        
        return response



class Live(object):
    """
    This DAO provides real data.  It requires further configuration, (conf)
    """
    pool = None

    def getURL(self, url, headers):
        if Live.pool == None:
            Live.pool = get_con_pool(get_con_pool(self._conf['IRWS_HOST'],
                                     self._conf['IRWS_KEY_FILE'],
                                     self._conf['IRWS_CERT_FILE'],
                                     max_pool_size= IRWS_MAX_POOL_SIZE))
        return get_live_url(Live.pool, 'GET',
                            self._conf['IRWS_HOST'],
                            url, headers=headers,
                            service_name='irws')

    def putURL(self, url, headers, body):
        if Live.pool is None:
            Live.pool = self._get_pool()

        return get_live_url(Live.pool, 'PUT',
                            self._conf['IRWS_HOST'],
                            url, headers=headers, body=body,
                            service_name='irws')

