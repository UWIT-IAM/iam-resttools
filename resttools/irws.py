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


# json classes
import json

import datetime
import dateutil.parser

import os
import string
import time
import re
import random
import copy


from resttools.dao import IRWS_DAO
from resttools.models.irws import UWNetId
from resttools.models.irws import Subscription
from resttools.models.irws import Person
from resttools.models.irws import HeppsPerson
from resttools.models.irws import SdbPerson
from resttools.models.irws import Pac
from resttools.models.irws import Name
from resttools.models.irws import QnA

from resttools.exceptions import DataFailureException

import logging
logger = logging.getLogger(__name__)

class IRWS(object):

    def __init__(self, conf):

        self._service_name = conf['SERVICE_NAME']
        self._conf = conf
        self.new_ids = set([])

    def _get_code_from_error(self, message):
        try:
           code = int(json.loads(message)['error']['code'])
        except:
           code = (-1)
        return code

    def get_uwnetid(self, eid=None, regid=None, netid=None, source=None, status=None, ret_array=False):
        """
        Returns an irws.UWNetid object for the given netid or regid.  If the
        netid isn't found, nothing will be returned.  If there is an error
        communicating with the IRWS, a DataFailureException will be thrown.
        if 'all' an array is returned with all the matching netids.
        """

        status_str = ''
        if status!=None:
            status_str = '&status=%d' % status
        dao = IRWS_DAO(self._conf)
        if eid!=None and source!=None:
            url = "/%s/v1/uwnetid?validid=%d=%s%s" % (self._service_name, source, eid, status_str)
        elif regid!=None:
            url = "/%s/v1/uwnetid?validid=regid=%s%s" % (self._service_name, regid, status_str)
        elif netid!=None:
            url = "/%s/v1/uwnetid?validid=uwnetid=%s%s" % (self._service_name, netid, status_str)
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

    def get_person(self, netid=None, regid=None, eid=None):
        """
        Returns an irws.Person object for the given netid or regid.  If the
        netid isn't found, nothing will be returned.  If there is an error
        communicating with the IRWS, a DataFailureException will be thrown.
        """
        dao = IRWS_DAO(self._conf)
        url = None 
        if netid!=None:
            url = "/%s/v1/person?uwnetid=%s" % (self._service_name, netid.lower())
        elif regid!=None:
            url = "/%s/v1/person?validid=regid=%s" % (self._service_name, regid)
        elif eid!=None:
            url = "/%s/v1/person?validid=1=%s" % (self._service_name, eid)
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

        dao = IRWS_DAO(self._conf)
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
        dao = IRWS_DAO(self._conf)

        url = "/%s/v1/person/hepps/%s" % (self._service_name, eid)
        response = dao.getURL(url, {"Accept": "application/json"})

        if response.status == 404:
            return None

        if response.status != 200:
            raise IRWSConnectionError(url, response.status, response.data)

        return  self._hepps_person_from_json(response.data)
        

    def get_sdb_person(self, vid):
        """
        Returns an irws.SdbPerson object for the given eid.
        If the person is not a student, returns None.
        If the netid isn't found, throws IRWSNotFound.
        If there is an error communicating with the IRWS, throws IRWSConnectionError.
        """
        dao = IRWS_DAO(self._conf)

        url = "/%s/v1/person/sdb/%s" % (self._service_name, vid)
        response = dao.getURL(url, {"Accept": "application/json"})

        if response.status == 404:
            return None

        if response.status != 200:
            raise IRWSConnectionError(url, response.status, response.data)

        return  self._sdb_person_from_json(response.data)
        

    def get_subscription(self, netid, subscription):
        """
        Returns an irws.Subscription object for the given netid.  If the
        netid isn't found, nothing will be returned.  If there is an error
        communicating with the IRWS, a DataFailureException will be thrown.
        """
        dao = IRWS_DAO(self._conf)
        url = "/%s/v1/subscription?uwnetid=%s&subscription=%d" % (self._service_name, netid.lower(), subscription)
        response = dao.getURL(url, {"Accept": "application/json"})

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        return self._subscription_from_json(response.data)

    def put_pac(self, eid):
        """
        Creates a PAC for the employee.  Returns the Pac.
        """
        dao = IRWS_DAO(self._conf)
        url = "/%s/v1/person/hepps/%s/pac" % (self._service_name, eid)
        response = dao.putURL(url, {"Accept": "application/json"}, '')

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        return self._pac_from_json(response.data)


    def get_qna(self, netid):
        """
        Returns a list irws.QnA for the given netid.
        """
        dao = IRWS_DAO(self._conf)

        url = "/%s/v1/qna?uwnetid=%s" % (self._service_name, netid)
        response = dao.getURL(url, {"Accept": "application/json"})

        if response.status == 404:
            return None

        if response.status != 200:
            raise IRWSConnectionError(url, response.status, response.data)

        return  self._qna_from_json(response.data)
        
    def _hepps_person_from_json(self, data):
        """
        Internal method, for creating the HeppsPerson object.
        """
        person_data = json.loads(data)['person'][0]
        person = HeppsPerson()
        person.validid = person_data['validid']
        person.regid = person_data['regid']
        if 'studentid' in person_data: person.studentid = person_data['studentid']
        if 'birthdate' in person_data: person.birthdate = person_data['birthdate']

        person.fname = person_data['fname']
        person.lname = person_data['lname']

        person.hepps_type = person_data['hepps_type']
        person.hepps_status = person_data['hepps_status']
        person.category_code = person_data['category_code']
        person.category_name = person_data['category_name']
        person.source_code = person_data['source_code']
        person.source_name = person_data['source_name']
        person.status_code = person_data['status_code']
        person.status_name = person_data['status_name']
        if 'contact_email' in person_data:
            person.contact_email = person_data['contact_email']
        if 'org_supervisor' in person_data:
            person.org_supervisor = person_data['org_supervisor']

        if 'pac' in person_data: person.pac = person_data['pac']

        if 'wp_publish' in person_data: person.wp_publish = person_data['wp_publish']
        else: person.wp_publish = 'Y'
        return person

    def _sdb_person_from_json(self, data):
        """
        Internal method, for creating the SdbPerson object.
        """
        person_data = json.loads(data)['person'][0]
        person = SdbPerson()
        person.validid = person_data['validid']
        person.regid = person_data['regid']
        person.studentid = person_data['studentid']
        if 'birthdate' in person_data: person.birthdate = person_data['birthdate']

        person.fname = person_data['fname']
        person.lname = person_data['lname']

        person.category_code = person_data['category_code']
        person.category_name = person_data['category_name']
        person.source_code = person_data['source_code']
        person.source_name = person_data['source_name']
        person.status_code = person_data['status_code']
        person.status_name = person_data['status_name']

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

    def _name_from_json(self, data):
        nd = json.loads(data)['name'][0]
        name = Name()
        name.validid = nd['validid']
        if 'formal_cname' in nd: name.formal_cname = nd['formal_cname']
        if 'formal_fname' in nd: name.formal_fname = nd['formal_fname']
        if 'formal_sname' in nd: name.formal_lname = nd['formal_sname']
        if 'formal_privacy' in nd: name.formal_privacy = nd['formal_privacy']
        if 'display_cname' in nd: name.display_cname = nd['display_cname']
        if 'display_fname' in nd: name.display_fname = nd['display_fname']
        if 'display_mname' in nd: name.display_mname = nd['display_mname']
        if 'display_sname' in nd: name.display_lname = nd['display_sname']
        if 'display_privacy' in nd: name.display_privacy = nd['display_privacy']
        return name


    def _qna_from_json(self, data):
        q_list = json.loads(data)['qna']
        ret = []
        for q in q_list:
            qna = QnA()
            qna.uwnetid = q['uwnetid']
            qna.ordinal = q['ordinal']
            qna.question = q['question']
            qna.answer = q['answer']
            ret.append(qna)
        return ret


