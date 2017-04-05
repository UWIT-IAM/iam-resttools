# resttools implementation for non-django applications
from resttools.dao_implementation.irws import File as IRWSFile
from resttools.dao_implementation.irws import Live as IRWSLive
from resttools.dao_implementation.nws import File as NWSFile
from resttools.dao_implementation.nws import Live as NWSLive
from resttools.dao_implementation.gws import File as GWSFile
from resttools.dao_implementation.gws import Live as GWSLive
from resttools.dao_implementation.ntfyws import File as NTFYWSFile
from resttools.dao_implementation.ntfyws import Live as NTFYWSLive


class DAO_BASE(object):

    def __init__(self, conf):
        self._conf = conf
        self._run_mode = conf['RUN_MODE']

    def _getURL(self, service, url, headers):
        dao = self._getDAO()
        response = dao.getURL(url, headers)
        return response

    def _postURL(self, service, url, headers, body=None):
        dao = self._getDAO()
        response = dao.postURL(url, headers, body)
        return response

    def _deleteURL(self, service, url, headers):
        dao = self._getDAO()
        response = dao.deleteURL(url, headers)
        return response

    def _putURL(self, service, url, headers, body=None):
        dao = self._getDAO()
        response = dao.putURL(url, headers, body)
        return response


class IRWS_DAO(DAO_BASE):
    def getURL(self, url, headers):
        return self._getURL('irws', url, headers)

    def putURL(self, url, headers, body):
        return self._putURL('irws', url, headers, body)

    def postURL(self, url, headers, body):
        return self._postURL('irws', url, headers, body)

    def deleteURL(self, url, headers):
        return self._deleteURL('irws', url, headers)

    def _getDAO(self):
        if self._run_mode == 'Live':
            return IRWSLive(self._conf)
        return IRWSFile(self._conf)


class NWS_DAO(DAO_BASE):
    def getURL(self, url, headers):
        return self._getURL('nws', url, headers)

    def postURL(self, url, headers, body):
        return self._postURL('nws', url, headers, body)

    def _getDAO(self):
        if self._run_mode == 'Live':
            return NWSLive(self._conf)
        return NWSFile(self._conf)


class GWS_DAO(DAO_BASE):
    def getURL(self, url, headers):
        return self._getURL('gws', url, headers)

    def putURL(self, url, headers, body):
        return self._putURL('gws', url, headers, body)

    def deleteURL(self, url, headers):
        return self._deleteURL('gws', url, headers)

    def _getDAO(self):
        if self._run_mode == 'Live':
            return GWSLive(self._conf)
        return GWSFile(self._conf)


class NTFYWS_DAO(DAO_BASE):
    def postURL(self, url, headers, body):
        return self._postURL('ntfyws', url, headers, body)

    def _getDAO(self):
        if self._run_mode == 'Live':
            return NTFYWSLive(self._conf)
        return NTFYWSFile(self._conf)
