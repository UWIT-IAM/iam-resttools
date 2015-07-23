"""
This is the interface for interacting with the UW NetID Web Service.
"""

from resttools.dao import NWS_DAO
from resttools.models.nws import UWNetIdAdmin
from urllib import urlencode
from lxml import etree
import re

import logging
logger = logging.getLogger(__name__)

class NWS(object):

    def __init__(self, conf, actas=None):
        self._service_name = 'nws'
        self._conf = conf


    def get_netid_admins(self, netid):
        """
        Returns a list of NetidAdmin objects for the netid
        """

        dao = NWS_DAO(self._conf)
        url = "/nws/v1/uwnetid/%s/admin" % netid
        response = dao.getURL(url, self._headers({"Accept": "text/xml"}))

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        return self._admins_from_xml(response.data)



    def _admins_from_xml(self, data):
        e_adms= etree.fromstring(data).find('adminList')
        e_adm_list = e_adms.findall('uwNetID')

        admins = []
        for admin in e_adm_list:
            name = admin.find('name').text
            role = admin.find('role').text
            admins.append(UWNetIdAdmin(name=name, role=role))
        return admins


    def _headers(self, headers):
        # could auto-add headers here
        return headers

    def _add_header(self, headers, header, value):
        if not headers:
            return { header: value }

        headers[header] = value
        return headers
