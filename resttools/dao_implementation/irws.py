"""
Contains IRWS DAO implementations.
"""
from resttools.mock.mock_http import MockHTTP
import json
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
    _cache_db = {}

    def __init__(self, conf):
        self._conf = conf
        if 'MAX_POOL_SIZE' in conf:
            self._max_pool_size = conf['MAX_POOL_SIZE']

    def getURL(self, url, headers):
        logger.debug('file irws get url: ' + url)
        if url in File._cache_db:
            logger.debug('using cache')
            response = MockHTTP()
            response.data = File._cache_db[url]
            response.status = 200
            return response
        response = get_mockdata_url("irws", self._conf, url, headers)
        if response.status == 404:
            logger.debug('status 404')
            response.data = '{"error": {"code": "7000","message": "No record matched"}}'
        return response

    def putURL(self, url, headers, body):
        logger.debug('file irws put url: ' + url)

        # eat an optional "?-reflect", it will affect our response
        reflect = re.search(r'([?&])(-reflect)([&]*)', url)
        if reflect:
            if reflect.end(3) == reflect.start(3):
                url = url[:reflect.start(1)]
            else:
                url = url[:reflect.start(1) + 1] + url[reflect.start(3) + 1:]

        response = get_mockdata_url("irws", self._conf, url, headers)
        if response.status != 404 or url in File._cache_db:
            # try set in cache
            cache_data = json.loads(File._cache_db.get(url, None) or
                                    response.data)
            put_data = json.loads(body)
            key, items = next(iter(put_data.items()))
            put_section = items[0]
            if key == 'name':
                # fake a cname update
                name_parts = [put_section.get('preferred_{}name'.format(x), '')
                              for x in ('f', 'm', 's')]
                put_section['preferred_cname'] = ' '.join(x for x in name_parts if x)
            # update the put data and leave everything else in place
            cache_data[key][0].update(put_section)
            if 'entity.profile' in cache_data and 'pronoun' in cache_data['entity.profile'][0]:
                if cache_data['entity.profile'][0]['pronoun'] == 'attribute=101':
                    cache_data['entity.profile'][0]['pronoun'] = 'she/her/hers'
                elif cache_data['entity.profile'][0]['pronoun'] == 'attribute=102':
                    cache_data['entity.profile'][0]['pronoun'] = 'he/him/his'
                elif cache_data['entity.profile'][0]['pronoun'] == 'attribute=103':
                    cache_data['entity.profile'][0]['pronoun'] = 'they/them/theirs'
                elif cache_data['entity.profile'][0]['pronoun'] == 'attribute=104':
                    cache_data['entity.profile'][0]['pronoun'] = 'use my name'
                elif cache_data['entity.profile'][0]['pronoun'] == '':
                    del cache_data['entity.profile'][0]['pronoun']
            File._cache_db[url] = json.dumps(cache_data)
            # return an irws-style put response
            if reflect:
                response.data = File._cache_db[url]
            else:
                response.data = '{"cached": {"code": "0000","message": "put cached in mock data"}}'
            response.status = 200

        return response

    def postURL(self, url, headers, body):
        return self.putURL(url, headers, body)

    def deleteURL(self, url, headers):
        logger.debug('file irws delete url: ' + url)
        response = get_mockdata_url("irws", self._conf, url, headers)
        # no status for deletes from mock
        response.status = 200
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

    # class attribute means you can't switch hosts/keys
    pool = None

    def getURL(self, url, headers):
        return get_live_url(self._get_pool(), 'GET',
                            self._conf['HOST'],
                            url, headers=headers,
                            service_name='irws')

    def deleteURL(self, url, headers):
        return get_live_url(self._get_pool(), 'DELETE',
                            self._conf['HOST'],
                            url, headers=headers,
                            service_name='irws')

    def putURL(self, url, headers, body):
        return get_live_url(self._get_pool(), 'PUT',
                            self._conf['HOST'],
                            url, headers=headers, body=body,
                            service_name='irws')

    def postURL(self, url, headers, body):
        return get_live_url(self._get_pool(), 'POST',
                            self._conf['HOST'],
                            url, headers=headers, body=body,
                            service_name='irws')

    def _get_pool(self):
        if not Live.pool:
            Live.pool = get_con_pool(self._conf['HOST'],
                                     self._conf['KEY_FILE'],
                                     self._conf['CERT_FILE'],
                                     self._conf['CA_FILE'],
                                     max_pool_size=self._max_pool_size,
                                     verify_https=self._conf.get('VERIFY_HOST', True))
        return Live.pool
