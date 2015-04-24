# workday interfaces and tools - library
#

# connection pooling http client
import urllib3
from urllib3.connectionpool import HTTPSConnectionPool
from urllib3.exceptions import MaxRetryError
from urllib3.exceptions import SSLError
from urllib3.exceptions import ReadTimeoutError

# timeouts
connectTimeout = 20.0
readTimeout = 30.0

# xml parser
import xml.etree.cElementTree as ET
from xml.sax.saxutils import escape

# json classes
import simplejson as json

import ssl

import datetime
import dateutil.parser

import os
import string
import time
import re
import random
import copy


import settings

from dao import IRWS_DAO
from models.irws import UWNetId
from models.irws import Subscription
from models.irws import Person
from models.irws import HeppsPerson
from models.irws import Pac

from exceptions import DataFailureException

import logging
logger = logging.getLogger(__name__)

class IRWS(object):

    def __init__(self):

        self._service_name = settings.RESTTOOLS_IRWS_SERVICE_NAME
        self.new_ids = set([])


    def _get_code_from_error(self, message):
        try:
           code = int(json.loads(message)['error']['code'])
        except:
           code = (-1)
        return code

    def get_uwnetid(self, eid=None, regid=None, source=None, status=None, ret_array=False):
        """
        Returns an irws.UWNetid object for the given netid or regid.  If the
        netid isn't found, nothing will be returned.  If there is an error
        communicating with the IRWS, a DataFailureException will be thrown.
        if 'all' an array is returned with all the matching netids.
        """

        status_str = ''
        if status!=None:
            status_str = '&status=%d' % status
        source_str = ''
        dao = IRWS_DAO()
        if eid!=None and source!=None:
            url = "/%s/v1/uwnetid?validid=%d=%s%s" % (self._service_name, source, eid, status_str)
        elif regid!=None:
            url = "/%s/v1/uwnetid?validid=regid=%s%s" % (self._service_name, regid, status_str)
        else:
            return None
        response = dao.getURL(url, {"Accept": "application/json"})

        if response.status == 404:
            err = self._get_code_from_error(response.data)
            if err==7000:
                return None

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        id_data = json.loads(response.data)['uwnetid']
        if ret_array:
            ret = []
            for n in range(0,len(id_data)):
               ret.append(self._uwnetid_from_json_obj(id_data[n]))
            return ret
        else:
            return self._uwnetid_from_json_obj(id_data[0])

    def get_person(self, netid=None, regid=None):
        """
        Returns an irws.Person object for the given netid or regid.  If the
        netid isn't found, nothing will be returned.  If there is an error
        communicating with the IRWS, a DataFailureException will be thrown.
        """
        dao = IRWS_DAO()
        url = None 
        if netid!=None:
            url = "/%s/v1/person?uwnetid=%s" % (self._service_name, netid.lower())
        elif regid!=None:
            url = "/%s/v1/person?validid=regid=%s" % (self._service_name, regid)
        else:
            return None
        response = dao.getURL(url, {"Accept": "application/json"})

        if response.status == 404:
            err = self._get_code_from_error(response.data)
            if err==7000:
                return None

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        return self._person_from_json(response.data)

    def get_name_by_netid(self, netid):
        """
        Returns a resttools.irws.Name object for the given netid.  If the
        netid isn't found, nothing will be returned.  If there is an error
        communicating with the IRWS, a DataFailureException will be thrown.
        """
        if not self.valid_uwnetid(netid):
            raise InvalidNetID(netid)

        dao = IRWS_DAO()
        url = "/%s/v1/name/uwnetid=%s" % (self._service_name, netid.lower())
        response = dao.getURL(url, {"Accept": "application/json"})

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        return self._name_from_json(response.data)

    def get_hepps_person(self, eid):
        """
        Returns an irws.HeppsPerson object for the given eid.
        If the person is not an employee, returns None.
        If the netid isn't found, throws IRWSNotFound.
        If there is an error communicating with the IRWS, throws IRWSConnectionError.
        """
        dao = IRWS_DAO()

        url = "/%s/v1/person/hepps/%s" % (self._service_name, eid)
        response = dao.getURL(url, {"Accept": "application/json"})

        if response.status == 404:
            return None

        if response.status != 200:
            raise IRWSConnectionError(url, response.status, response.data)

        return  self._hepps_person_from_json(response.data)
        

    def get_subscription(self, netid, subscription):
        """
        Returns an irws.Subscription object for the given netid.  If the
        netid isn't found, nothing will be returned.  If there is an error
        communicating with the IRWS, a DataFailureException will be thrown.
        """
        dao = IRWS_DAO()
        url = "/%s/v1/subscription?uwnetid=%s&subscription=%d" % (self._service_name, netid.lower(), subscription)
        response = dao.getURL(url, {"Accept": "application/json"})

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        return self._subscription_from_json(response.data)

    def put_pac(self, eid):
        """
        Creates a PAC for the employee.  Returns the Pac.
        """
        dao = IRWS_DAO()
        url = "/%s/v1/person/hepps/%s/pac" % (self._service_name, eid)
        response = dao.putURL(url, {"Accept": "application/json"}, '')

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        return self._pac_from_json(response.data)


    def _hepps_person_from_json(self, data):
        """
        Internal method, for creating the HeppsPerson object.
        """
        person_data = json.loads(data)['person'][0]
        person = HeppsPerson()
        person.validid = person_data['validid']
        person.regid = person_data['regid']
        if 'studentid' in person_data: person.studentid = person_data['studentid']

        person.fname = person_data['fname']
        person.lname = person_data['lname']

        person.category_code = person_data['category_code']
        person.category_name = person_data['category_name']
        if 'contact_email' in person_data:
            person.contact_email = person_data['contact_email']
        if 'org_supervisor' in person_data:
            person.org_supervisor = person_data['org_supervisor']

        if 'pac' in person_data: person.pac = person_data['pac']

        if 'wp_publish' in person_data: person.wp_publish = person_data['wp_publish']
        else: person.wp_publish = 'Y'
        return person

    def _person_from_json(self, data):
        persj = json.loads(data)['person'][0]
        idj = persj['identity']
        person = Person()
        person.regid = idj['regid']
        person.lname = idj['lname']
        person.fname = idj['fname']
        person.identifiers = copy.deepcopy(idj['identifiers'])
        return person

    def _uwnetid_from_json_obj(self, id_data):
        uwnetid = UWNetId()
        uwnetid.uwnetid = id_data['uwnetid']
        uwnetid.validid = id_data['validid']
        uwnetid.uid = id_data['uid']
        return uwnetid

    def _subscription_from_json(self, data):
        sub_data = json.loads(data)['subscription'][0]
        subscription = Subscription()
        subscription.uwnetid = sub_data['uwnetid']
        subscription.subscription_code = sub_data['subscription_code']
        subscription.subscription_name = sub_data['subscription_name']
        return subscription

    def _pac_from_json(self, data):
        pac_data = json.loads(data)['person'][0]
        pac = Pac()
        pac.pac = pac_data['pac']
        pac.expiration = pac_data['expiration']
        return pac



