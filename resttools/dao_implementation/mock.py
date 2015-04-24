import sys
import os
from os.path import abspath, dirname
import re
import json
import time
import socket
import settings
from resttools.mock.mock_http import MockHTTP

"""
A centralized the mock data access
"""
fs_encoding = sys.getfilesystemencoding() or sys.getdefaultencoding()
app_resource_dirs = []

import logging
logger = logging.getLogger(__name__)


def get_mockdata_url(service_name, implementation_name,
                     url, headers):
    """
    :param service_name:
        possible "irws", "pws", "gws", etc.
    :param implementation_name:
        possible values: "file", etc.
    """

    file_path = None
    success = False
    start_time = time.time()

    dir_base = dirname(__file__)
    app_root = abspath(dir_base)
    response = _load_resource_from_path(app_root, service_name, implementation_name, url, headers)
    if response:
        return response

    # If no response has been found in any installed app, return a 404
    logger.info("404 for url %s, path: %s" % (url, "resources/%s/%s/%s" %(service_name, implementation_name, convert_to_platform_safe(url))))
    response = MockHTTP()
    response.status = 404
    return response

def _load_resource_from_path(app_root, service_name, implementation_name,
                                url, headers):

    mock_root = app_root + '/../mock' 
    std_root = mock_root + '/' + service_name + '/' + implementation_name
    if hasattr(settings, 'RESTTOOLS_MOCK_ROOT'):
        mock_root = settings.RESTTOOLS_MOCK_ROOT
    root = mock_root + '/' + service_name + '/' + implementation_name

    if url == "///":
        # Just a placeholder to put everything else in an else.
        # If there are things that need dynamic work, they'd go here
        pass
    else:
        try:
            file_path = convert_to_platform_safe(root + url)
            print 'try: ' + file_path
            if os.path.isdir(file_path):
                file_path = file_path + '.resource'
            handle = open(file_path)
        except IOError:
            try:
                file_path = convert_to_platform_safe(std_root + url)
                if os.path.isdir(file_path):
                    file_path = file_path + '.resource'
                handle = open(file_path)
            except IOError:
                return

        logger.debug("URL: %s; File: %s" % (url, file_path))

        response = MockHTTP()
        response.status = 200
        response.data = handle.read()
        response.headers = {"X-Data-Source": service_name + " file mock data", }

        try:
            headers = open(handle.name + '.http-headers')
            file_values = json.loads(headers.read())

            if "headers" in file_values:
                response.headers = dict(response.headers.items() + file_values['headers'].items())

                if 'status' in file_values:
                    response.status = file_values['status']

            else:
                response.headers = dict(response.headers.items() + file_values.items())

        except IOError:
            pass

        return response



def post_mockdata_url(service_name, implementation_name,
                     url, headers, body,
                     dir_base = dirname(__file__)):
    """
    :param service_name:
        possible "sws", "pws", "book", "hfs", etc.
    :param implementation_name:
        possible values: "file", etc.
    """
    #Currently this post method does not return a response body
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


def put_mockdata_url(service_name, implementation_name,
                     url, headers, body,
                     dir_base = dirname(__file__)):
    """
    :param service_name:
        possible "sws", "pws", "book", "hfs", etc.
    :param implementation_name:
        possible values: "file", etc.
    """
    #Currently this put method does not return a response body
    response = MockHTTP()
    if body is not None:
        response.status = 204
        response.headers = {"X-Data-Source": service_name + " file mock data", "Content-Type": headers['Content-Type']}
    else:
        response.status = 400
        response.data = "Bad Request: no POST body"
    return response


def delete_mockdata_url(service_name, implementation_name,
                     url, headers,
                     dir_base = dirname(__file__)):
    """
    :param service_name:
        possible "sws", "pws", "book", "hfs", etc.
    :param implementation_name:
        possible values: "file", etc.
    """
    #Http response code 204 No Content:
    #The server has fulfilled the request but does not need to return an entity-body
    response = MockHTTP()
    response.status = 204

    return response

def convert_to_platform_safe(dir_file_name):
    """
    :param dir_file_name: a string to be processed
    :return: a string with all the reserved characters replaced
    """
    return  re.sub('[\?|<>=:*,;+&"@]', '_', dir_file_name)
