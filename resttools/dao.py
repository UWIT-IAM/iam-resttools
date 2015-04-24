# resttools implementation for non-django applications

import settings 

from resttools.mock.mock_http import MockHTTP
from resttools.dao_implementation.irws import File as IRWSFile
from resttools.dao_implementation.irws import Live as IRWSLive
from resttools.dao_implementation.gws import File as GWSFile
from resttools.dao_implementation.gws import Live as GWSLive

class DAO_BASE(object):
             
    def __init__(self, conf):
        self._conf = conf

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

    def _getDAO(self):
        if settings.RUN_MODE=='Live':
            return IRWSLive(self._conf)
        return IRWSFile(self._conf)



class GWS_DAO(DAO_BASE):
    def getURL(self, url, headers):
        return self._getURL('gws', url, headers)

    def putURL(self, url, headers, body):
        return self._putURL('gws', url, headers, body)

    def deleteURL(self, url, headers, body):
        return self._deleteURL('gws', url, headers, body)

    def _getDAO(self):
        if settings.RUN_MODE=='Live':
            return GWSLive(self._conf)
        return GWSFile(self._conf)

