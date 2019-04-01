import requests
import time
from logging import getLogger
logger = getLogger(__name__)


class Client(requests.Session):
    base_url = ''
    timeout = 15

    def __init__(self, base_url='', cert=()):
        super(Client, self).__init__()
        if base_url:
            self.base_url = base_url
        if cert:
            self.cert = cert

    def request(self, method, url, *args, **kwargs):
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout
        url = self.base_url + url
        start_time = time.time()
        status = None
        try:
            response = self._request_retry_loop(method, url, *args, **kwargs)
            status = response.status_code
        finally:
            elapsed = time.time() - start_time
            self.log_result(method, url, status, elapsed)
        return response

    def _request_retry_loop(self, method, url, *args, **kwargs):
        """
        Retry on requests.ConnectionError three times before giving up.
        """
        request = super(Client, self).request
        for _ in range(2):
            try:
                return request(method, url, *args, **kwargs)
            except requests.ConnectionError:
                logger.info(f'ConnectionError, attempting {method} of {url}')
        return request(method, url, *args, **kwargs)
    
    def log_result(self, method, url, status, elapsed):
        if not status or status >= 500:
            log = logger.error
        elif elapsed > 5:
            log = logger.warning
        else:
            log = logger.debug
        log(f'{method} {url} {status} {elapsed:0.3f} seconds')


class ConfDict:
    def __init__(self, conf={}, **kwargs):
        if 'KEY_FILE' in conf and 'CERT_FILE' in conf:
            kwargs['cert'] = conf.get('CERT_FILE'), conf.get('KEY_FILE')
        cname = self.__class__.__name__
        if cname == 'nws' and 'HOST' in conf and 'SERVICE_NAME' in conf:
            kwargs['base_url'] = '%s/%s/v1' % (conf['HOST'], conf('SERVICE_NAME'))
        if cname == 'irws' and 'HOST' in conf and 'SERVICE_NAME' in conf:
            kwargs['base_url'] = '%s/%s/v2' % (conf['HOST'], conf('SERVICE_NAME'))
        super(ConfDict, self).__init__(**kwargs)