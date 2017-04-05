"""
Provides access to the http connection pools and
connections for live data from a web service

"""
import ssl
from six.moves.urllib.parse import urlparse
from urllib3 import connection_from_url


def get_con_pool(host,
                 key_file=None,
                 cert_file=None,
                 ca_file=None,
                 socket_timeout=15.0,
                 max_pool_size=3,
                 verify_https=True):
    """
    Return a ConnectionPool instance of given host
    :param socket_timeout:
        socket timeout for each connection in seconds
    """
    kwargs = {
        "timeout": socket_timeout,
        "maxsize": max_pool_size,
        "block": True,
        }

    if key_file is not None and cert_file is not None:
        kwargs["key_file"] = key_file
        kwargs["cert_file"] = cert_file

    if urlparse(host).scheme == "https":
        kwargs["ssl_version"] = ssl.PROTOCOL_TLSv1
        if verify_https:
            kwargs["cert_reqs"] = "CERT_REQUIRED"
            kwargs["ca_certs"] = ca_file

    return connection_from_url(host, **kwargs)


def get_live_url(con_pool,
                 method,
                 host,
                 url,
                 headers,
                 retries=3,
                 body=None,
                 service_name=None):
    """
    Return a connection from the pool and perform an HTTP request.
    :param con_pool:
        is the http connection pool associated with the service
    :param method:
        HTTP request method (such as GET, POST, PUT, etc.)
    :param host:
        the url of the server host.
    :param headers:
        headers to include with the request
    :param body:
        the POST, PUT body of the request
    """
    timeout = con_pool.timeout
    response = con_pool.urlopen(method, url, body=body, headers=headers, retries=retries, timeout=timeout)
    return response
