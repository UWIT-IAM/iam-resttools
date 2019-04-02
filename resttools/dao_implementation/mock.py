"""
A centralized the mock data access
"""
import sys
import os
from os.path import abspath, dirname
import re
import json
import logging
import requests
from six.moves.urllib import parse
from resttools.mock.mock_http import MockHTTP as MockResponse


class MockHttp(requests.Session):
    def request(self, method, url, *args, **kwargs):
        base_url = getattr(self, 'base_url', '')
        if url.startswith(base_url):
            url = url.split(base_url)[1]
        if 'params' in kwargs:
            url = url + '?' + parse.urlencode(kwargs['params'])

        service_name = self.__class__.__name__.lower()
        dir_base = dirname(__file__)
        app_root = abspath(dir_base)
        response = _load_resource_from_path(app_root, service_name, {}, url, self.headers)
        if response:
            return response

        # If no response has been found in any installed app, return a 404
        logger = logging.getLogger(__name__)
        logger.debug("404 for url %s" % url)
        response = MockResponse()
        response.status_code = 404
        return response


class MockIrws(MockHttp):
    _cache = {}

    def request(self, method, url, *args, **kwargs):
        if method == 'GET' and url in self._cache:
            return self._cache[url]
        elif method in ('PUT', 'POST'):
            response = super(MockIrws, self).request('GET', url, *args, **kwargs)
            if response.status_code != 200:
                return response
            data = response.json()
            key = next(iter(kwargs['json']), None)
            if key:
                data[key][0].update(kwargs['json'][key][0])
            response.content = json.dumps(data)
            self._cache[url] = response
            return response
        return super(MockIrws, self).request(method, url, *args, **kwargs)


def _load_resource_from_path(app_root, service_name, conf, url, headers):

    logger = logging.getLogger(__name__)
    mock_root = os.path.realpath(os.path.join(app_root, '../mock'))
    std_root = os.path.join(mock_root, service_name)
    if 'MOCK_ROOT' in conf and conf['MOCK_ROOT'] is not None:
        mock_root = conf['MOCK_ROOT']
    root = os.path.join(mock_root, service_name)

    try:
        file_path = convert_to_platform_safe(root + url)
        logger.debug('try1: ' + file_path)
        if os.path.isdir(file_path):
            file_path = file_path + '.resource'
        handle = open(file_path)
    except IOError:
        if std_root is not mock_root:
            try:
                file_path = convert_to_platform_safe(std_root + url)
                logger.debug('try2: ' + file_path)
                if os.path.isdir(file_path):
                    file_path = file_path + '.resource'
                handle = open(file_path)
            except IOError:
                return

    logger.debug("URL: %s; File: %s" % (url, file_path))

    response = MockResponse()
    response.status_code = 200
    data = handle.read()
    cut = data.find('MOCKDATA-MOCKDATA-MOCKDATA')
    if cut >= 0:
        data = data[(data.find('\n', cut)+1):]
    response.content = data
    response.headers = {"X-Data-Source": service_name + " file mock data", }

    return response



def convert_to_platform_safe(dir_file_name):
    """
    :param dir_file_name: a string to be processed
    :return: a string with all the reserved characters replaced
    """
    return re.sub('[?|<>=*,;+&"@]', '_', dir_file_name)
