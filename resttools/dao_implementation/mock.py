"""
A centralized the mock data access
"""
import sys
import os
from os.path import abspath, dirname
import re
import json
import logging
from resttools.mock.mock_http import MockHTTP
fs_encoding = sys.getfilesystemencoding() or sys.getdefaultencoding()
app_resource_dirs = []


def get_mockdata_url(service_name, conf,
                     url, headers):
    """
    :param service_name:
        possible "irws", "pws", "gws", etc.
    """
    dir_base = dirname(__file__)
    app_root = abspath(dir_base)
    response = _load_resource_from_path(app_root, service_name, conf, url, headers)
    if response:
        return response

    # If no response has been found in any installed app, return a 404
    logger = logging.getLogger(__name__)
    logger.debug("404 for url %s")
    response = MockHTTP()
    response.status = 404
    return response


def _load_resource_from_path(app_root, service_name, conf, url, headers):

    logger = logging.getLogger(__name__)
    mock_root = os.path.realpath(os.path.join(app_root, '../mock'))
    std_root = os.path.join(mock_root, service_name)
    if 'MOCK_ROOT' in conf and conf['MOCK_ROOT'] is not None:
        mock_root = conf['MOCK_ROOT']
    root = os.path.join(mock_root, service_name)

    if url == "///":
        # Just a placeholder to put everything else in an else.
        # If there are things that need dynamic work, they'd go here
        pass
    else:
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

        response = MockHTTP()
        response.status = 200
        data = handle.read()
        cut = data.find('MOCKDATA-MOCKDATA-MOCKDATA')
        if cut >= 0:
            data = data[(data.find('\n', cut)+1):]
        response.data = data
        response.headers = {"X-Data-Source": service_name + " file mock data", }

        try:
            headers = open(handle.name + '.http-headers')
            data = headers.read()
            cut = data.find('MOCKDATA-MOCKDATA-MOCKDATA')
            if cut >= 0:
                data = data[(data.find('\n', cut) + 1):]
            file_values = json.loads(data)

            if "headers" in file_values:
                response.headers = dict(response.headers.items() + file_values['headers'].items())

            if 'status' in file_values:
                response.status = file_values['status']

            else:
                response.headers = dict(response.headers.items() + file_values.items())

        except IOError:
            pass

        return response


def post_mockdata_url(service_name, conf, url, headers, body, dir_base=dirname(__file__)):
    """
    :param service_name:
        possible "sws", "pws", "book", "hfs", etc.
    """
    # Currently this post method does not return a response body
    response = MockHTTP()
    if body is not None:
        if "dispatch" in url:
            response.status = 200
        else:
            response.status = 201
        response.headers = {"X-Data-Source": service_name + " file mock data", "Content-Type": headers['Content-Type']}
    else:
        response.status = 400
        response.data = "Bad Request: no POST body"
    return response


def put_mockdata_url(service_name, conf, url, headers, body, dir_base=dirname(__file__)):
    """
    :param service_name:
        possible "sws", "pws", "book", "hfs", etc.
    """
    # Currently this put method does not return a response body
    response = MockHTTP()
    if body is not None:
        response.status = 204
        response.headers = {"X-Data-Source": service_name + " file mock data", "Content-Type": headers['Content-Type']}
    else:
        response.status = 400
        response.data = "Bad Request: no POST body"
    return response


def delete_mockdata_url(service_name, conf, url, headers, dir_base=dirname(__file__)):
    """
    :param service_name:
        possible "sws", "pws", "book", "hfs", etc.
    """
    # Http response code 204 No Content:
    # The server has fulfilled the request but does not need to return an entity-body
    response = MockHTTP()
    response.status = 204

    return response


def convert_to_platform_safe(dir_file_name):
    """
    :param dir_file_name: a string to be processed
    :return: a string with all the reserved characters replaced
    """
    return re.sub('[?|<>=*,;+&"@]', '_', dir_file_name)
