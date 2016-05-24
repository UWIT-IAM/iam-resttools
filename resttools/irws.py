# IRWS service interface
#

import os
import string
import time
import re
import random
import copy
from urllib import quote_plus

import json

from resttools.dao import IRWS_DAO
from resttools.models.irws import UWNetId
from resttools.models.irws import Regid
from resttools.models.irws import Subscription
from resttools.models.irws import Person
from resttools.models.irws import Profile
from resttools.models.irws import UWhrPerson
from resttools.models.irws import SdbPerson
from resttools.models.irws import CascadiaPerson
from resttools.models.irws import SccaPerson
from resttools.models.irws import SupplementalPerson
from resttools.models.irws import Pac
from resttools.models.irws import Name
from resttools.models.irws import QnA
from resttools.models.irws import GenericPerson
from resttools.models.irws import PDSEntry

from resttools.exceptions import DataFailureException, InvalidIRWSName
from resttools.exceptions import ResourceNotFound, BadInput

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

    def _clean(self, arg):
        if arg is not None:
            arg = quote_plus(arg)
        return arg

    # v2 - no change
    def get_uwnetid(self, eid=None, regid=None, netid=None, source=None, status=None, ret_array=False):
        """
        Returns an irws.UWNetid object for the given netid or regid.  If the
        netid isn't found, nothing will be returned.  If there is an error
        communicating with the IRWS, a DataFailureException will be thrown.
        if 'all' an array is returned with all the matching netids.
        """
        eid = self._clean(eid)
        regid = self._clean(regid)
        netid = self._clean(netid)

        status_str = ''
        if status is not None:
            status_str = '&status=%d' % status
        dao = IRWS_DAO(self._conf)
        if eid is not None and source is not None:
            url = "/%s/v2/uwnetid?validid=%d=%s%s" % (self._service_name, source, eid, status_str)
        elif regid is not None:
            url = "/%s/v2/uwnetid?validid=regid=%s%s" % (self._service_name, regid, status_str)
        elif netid is not None:
            url = "/%s/v2/uwnetid?validid=uwnetid=%s%s" % (self._service_name, netid, status_str)
        else:
            return None
        response = dao.getURL(url, {"Accept": "application/json"})

        if response.status == 404:
            return [] if ret_array else None

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        id_data = json.loads(response.data)['uwnetid']
        if ret_array:
            ret = []
            for n in range(0, len(id_data)):
                ret.append(self._uwnetid_from_json_obj(id_data[n]))
            return ret
        else:
            return self._uwnetid_from_json_obj(id_data[0])

    # v2 - no change
    def get_person(self, netid=None, regid=None, eid=None):
        """
        Returns an irws.Person object for the given netid or regid.  If the
        netid isn't found, nothing will be returned.  If there is an error
        communicating with the IRWS, a DataFailureException will be thrown.
        """
        netid = self._clean(netid)
        regid = self._clean(regid)
        eid = self._clean(eid)

        dao = IRWS_DAO(self._conf)
        url = None
        if netid is not None:
            url = "/%s/v2/person?uwnetid=%s" % (self._service_name, netid.lower())
        elif regid is not None:
            url = "/%s/v2/person?validid=regid=%s" % (self._service_name, regid)
        elif eid is not None:
            url = "/%s/v2/person?validid=1=%s" % (self._service_name, eid)
        else:
            return None
        response = dao.getURL(url, {"Accept": "application/json"})

        if response.status == 404:
            return None

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        return self._person_from_json(response.data)

    def post_hr_person_by_netid(self, netid, wp_publish=None):
        """
        Update the whitepages publish value for a netid's employee record.
        """
        if wp_publish not in ('Y', 'N', 'E'):
            raise BadInput('Invalid publish option')

        url = self._get_hr_url(netid)
        if url:
            hr_data = {'person': [{'wp_publish': wp_publish}]}
            response = IRWS_DAO(self._conf).postURL(
                url, {"Accept": "application/json"}, json.dumps(hr_data))
            if response.status != 200:
                raise DataFailureException(url, response.status, response.data)
        else:
            raise ResourceNotFound('not an hr person: {}'.format(netid))
        source, eid = url.split('/')[-2:]
        return self.get_uwhr_person(eid, source=source)

    def _get_hr_url(self, netid):
        """
        Given a netid, return the absolute url for a person's employee record
        or None if not an employee.
        """
        person = self.get_person(netid=netid)
        hr_url = None
        if person:
            hr_url = next((url for key, url in person.identifiers.items()
                           if key in ('uwhr', 'hepps')),
                          None)
            if hr_url:
                hr_url = '/{}/v2{}'.format(self._service_name, hr_url)
        return hr_url

    # v2 - no change
    def get_regid(self, netid=None, regid=None):
        """
        Returns an irws.Regid object for the given netid or regid.  If the
        netid isn't found, nothing will be returned.  If there is an error
        communicating with the IRWS, a DataFailureException will be thrown.
        """
        regid = self._clean(regid)
        netid = self._clean(netid)

        dao = IRWS_DAO(self._conf)
        url = None
        if netid is not None:
            url = "/%s/v2/regid?uwnetid=%s" % (self._service_name, netid.lower())
        elif regid is not None:
            url = "/%s/v2/regid?validid=regid=%s" % (self._service_name, regid)
        else:
            return None
        response = dao.getURL(url, {"Accept": "application/json"})

        if response.status == 404:
            return None

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        return self._regid_from_json(response.data)

    # v2 - changes
    def get_pw_recover_info(self, netid):
        """
        Returns an irws.Profile object containing password recovery fields
        for the given netid or regid.  If the
        netid isn't found, nothing will be returned.  If there is an error
        communicating with the IRWS, a DataFailureException will be thrown.
        """
        netid = self._clean(netid)

        dao = IRWS_DAO(self._conf)
        url = "/%s/v2/profile/validid=uwnetid=%s" % \
            (self._service_name, netid.lower())
        response = dao.getURL(url, {"Accept": "application/json"})

        if response.status == 404:
            return None

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        return self._pw_recover_from_json(response.data)

    def put_pw_recover_info(self, netid, profile):
        """
        Updates recover info in netid's profile
        """
        netid = self._clean(netid)

        dao = IRWS_DAO(self._conf)
        url = "/%s/v2/profile/validid=uwnetid=%s" % (self._service_name, netid)
        response = dao.putURL(url, {"Content-type": "application/json"}, json.dumps(profile.json_data()))

        if response.status >= 500:
            raise DataFailureException(url, response.status, response.data)

        return response.status

    def get_name_by_netid(self, netid, rollup=False):
        """
        Returns a resttools.irws.Name object for the given netid.  If the
        netid isn't found, nothing will be returned.  If there is an error
        communicating with the IRWS, a DataFailureException will be thrown.
        """
        netid = self._clean(netid)

        dao = IRWS_DAO(self._conf)
        url = "/%s/v2/name/uwnetid=%s" % (self._service_name, netid.lower())
        if rollup:  # add rollup flag if requested
            url += "?-rollup"
        response = dao.getURL(url, {"Accept": "application/json"})

        if response.status == 404:
            return None

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        return self._name_from_json(response.data)

    def put_name_by_netid(self, netid, first=None, middle=None, last=None):
        name = self.valid_name_json(first=first, middle=middle, last=last)
        url = "/%s/v2/name/uwnetid=%s" % (self._service_name, netid.lower())
        response = IRWS_DAO(self._conf).putURL(
            url, {'Accept': 'application/json'}, name)
        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)
        return response.status

    def valid_name_json(self, first=None, middle=None, last=None):
        """Construct name json to put to IRWS name."""
        if any(not self._valid_name_part(x) for x in (first, middle, last)):
            raise InvalidIRWSName('name too long or has invalid characters')
        if any(not x for x in (first, last)):
            raise InvalidIRWSName('required fields cannot be empty')
        if len(' '.join(x for x in (first, middle, last) if x)) > 80:
            raise InvalidIRWSName(
                'complete display name cannot be longer than 80 characters')

        return json.dumps({'name': [{'display_fname': first,
                                     'display_mname': middle,
                                     'display_sname': last}]})

    def _valid_name_part(self, name):
        regex = r'^[\w !$&\'*\-,.?^_`{}~#+%]*$'
        return len(name) <= 64 and re.match(regex, name)

    def get_uwhr_person(self, eid, source='uwhr'):
        """
        Returns an irws.UWhrPerson object for the given eid.
        If the person is not an employee, returns None.
        If the netid isn't found, throws IRWSNotFound.
        If there is an error contacting IRWS, throws DataFailureException.
        """
        eid = self._clean(eid)
        source = self._clean(source)

        dao = IRWS_DAO(self._conf)
        url = "/%s/v2/person/%s/%s" % (self._service_name, source, eid)
        response = dao.getURL(url, {"Accept": "application/json"})

        if response.status == 404:
            return None

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        return self._uwhr_person_from_json(response.data)

    def get_sdb_person(self, sid):
        """
        Returns an irws.SdbPerson object for the given eid.
        If the person is not a student, returns None.
        If the netid isn't found, throws IRWSNotFound.
        If there is an error contacting IRWS, throws DataFailureException.
        """
        sid = self._clean(sid)

        dao = IRWS_DAO(self._conf)

        url = "/%s/v2/person/sdb/%s" % (self._service_name, sid)
        response = dao.getURL(url, {"Accept": "application/json"})

        if response.status == 404:
            return None

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        return self._sdb_person_from_json(response.data)

    def get_cascadia_person(self, id):
        """
        Returns an irws.CascadiaPerson object for the given id.
        If the netid isn't found, throws IRWSNotFound.
        If there is an error contacting IRWS, throws DataFailureException.
        """
        id = self._clean(id)

        dao = IRWS_DAO(self._conf)

        url = "/%s/v2/person/cascadia/%s" % (self._service_name, id)
        response = dao.getURL(url, {"Accept": "application/json"})

        if response.status == 404:
            return None

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        return self._cascadia_person_from_json(response.data)

    def get_scca_person(self, id):
        """
        Returns an irws.SccaPerson object for the given id.
        If the netid isn't found, throws IRWSNotFound.
        If there is an error contacting IRWS, throws DataFailureException.
        """
        id = self._clean(id)

        dao = IRWS_DAO(self._conf)

        url = "/%s/v2/person/scca/%s" % (self._service_name, id)
        response = dao.getURL(url, {"Accept": "application/json"})

        if response.status == 404:
            return None

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        return self._scca_person_from_json(response.data)

    def get_supplemental_person(self, id):
        """
        Returns an irws.SupplementalPerson object for the given id.
        If the netid isn't found, throws IRWSNotFound.
        If there is an error contacting IRWS, throws DataFailureException.
        """
        id = self._clean(id)

        dao = IRWS_DAO(self._conf)
        url = "/%s/v2/person/supplemental/%s" % (self._service_name, id)
        response = dao.getURL(url, {"Accept": "application/json"})

        if response.status == 404:
            return None

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        return self._supplemental_person_from_json(response.data)

    def get_generic_person(self, uri):
        """
        Returns an irws.GenericPerson object for the given uri.
        The uris come in from values in irws.Person.identifiers.
        Raises DataFailureExeption on error.
        """
        uri = quote_plus(uri, '/')

        dao = IRWS_DAO(self._conf)
        url = '/%s/v2%s' % (self._service_name, uri)
        response = dao.getURL(url, {'Accept': 'application/json'})

        if response.status == 404:
            return None
        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        return self._generic_person_from_json(response.data)

    def get_subscription(self, netid, subscription):
        """
        Returns an irws.Subscription object for the given netid.  If the
        netid isn't found, nothing will be returned.  If there is an error
        communicating with the IRWS, a DataFailureException will be thrown.
        """
        netid = self._clean(netid)

        dao = IRWS_DAO(self._conf)
        url = "/%s/v2/subscription?uwnetid=%s&subscription=%d" % (self._service_name, netid.lower(), subscription)
        response = dao.getURL(url, {"Accept": "application/json"})

        if response.status == 404:
            return None

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        return self._subscription_from_json(response.data)

    def get_pdsentry_by_netid(self, netid):
        """
            Returns an irws.PdsEntry object for the given netid.
            If the person doesn't have a pds entry, returns None.
            If the netid isn't found, throws #TODO
            If there is an error contacting IRWS, throws DataFailureException.
            """
        sid = self._clean(netid)

        dao = IRWS_DAO(self._conf)

        url = "/%s/v2/pdsentry/validid=uwnetid=%s" % (self._service_name, netid)
        response = dao.getURL(url, {"Accept": "application/json"})

        if response.status == 404:
            return None

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        return self._pdsentry_from_json(response.data)

    def put_pac(self, eid, source='uwhr'):
        """
        Creates a PAC for the employee.  Returns the Pac.
        """
        eid = self._clean(eid)
        source = self._clean(source)

        dao = IRWS_DAO(self._conf)
        url = "/%s/v2/person/%s/%s/pac?-force" % (self._service_name, source, eid)
        response = dao.putURL(url, {"Accept": "application/json"}, '')

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        return self._pac_from_json(response.data)

    def verify_sdb_pac(self, sid, pac):
        """
        Verifies a permanent student PAC. Returns 200 (ok) or 400 (no)
        """
        sid = self._clean(sid)
        pac = self._clean(pac)

        dao = IRWS_DAO(self._conf)
        url = "/%s/v2/person/sdb/%s?pac=%s" % (self._service_name, sid, pac)
        response = dao.getURL(url, {"Accept": "application/json"})

        if (response.status == 200 or response.status == 400 or response.status == 404):
            return response.status
        raise DataFailureException(url, response.status, response.data)

    def verify_sc_pin(self, netid, pin):
        """
        Verifies a service center one-time pin. Returns 200 (ok) or 400 (no).
        OK clears the pin.
        """
        netid = self._clean(netid)
        pin = self._clean(pin)

        dao = IRWS_DAO(self._conf)
        # make sure there is a pin subscription
        url = "/%s/v2/subscription/63/%s" % (self._service_name, netid)
        response = dao.getURL(url, {"Accept": "application/json"})
        if response.status == 200:
            sub = json.loads(response.data)['subscription'][0]
            # verify pending subscription and unexpired, unused pac
            if sub['status_code'] != '23' or sub['pac'] != 'Y':
                return 404
        else:
            return response.status

        url = "/%s/v2/subscribe/63/%s?action=1&pac=%s" % (self._service_name, netid, pin)
        response = dao.getURL(url, {"Accept": "application/json"})
        if response.status == 200:
            # delete the pac
            url = "/%s/v2/subscribe/63/%s?action=2" % (self._service_name, netid)
            response = dao.getURL(url, {"Accept": "application/json"})
            if response.status != 200:
                # the pin was good.  we return OK, but note the error
                logging.warn('Delete SC pin failed: %d' % response.status)
            return 200

        if (response.status == 400 or response.status == 404):
            return response.status
        raise DataFailureException(url, response.status, response.data)

    def get_qna(self, netid):
        """
        Returns a list irws.QnA for the given netid.
        """
        netid = self._clean(netid)

        dao = IRWS_DAO(self._conf)

        url = "/%s/v2/qna?uwnetid=%s" % (self._service_name, netid)
        response = dao.getURL(url, {"Accept": "application/json"})

        if response.status == 404:
            return None

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        return self._qna_from_json(response.data)

    def get_verify_qna(self, netid, answers):
        """
        Verifies that all answers are present and that all are correct.
        answers: dict ('ordinal': 'answer')
        """
        netid = self._clean(netid)

        dao = IRWS_DAO(self._conf)
        q_list = self.get_qna(netid)
        for q in q_list:
            if q.ordinal not in answers:
                logging.debug('q %s, no answer' % q.ordinal)
                return False
            ans = re.sub(r'\W+', '', answers[q.ordinal])
            url = "/%s/v2/qna/%s/%s/check?ans=%s" % (self._service_name, q.ordinal, netid, quote_plus(ans))
            response = dao.getURL(url, {"Accept": "application/json"})
            if response.status == 404:
                logging.debug('q %s, wrong answer' % q.ordinal)
                return False
            if response.status != 200:
                logging.debug('q %s, error return: %d' % (q.ordinal, response.status))
                return False
            logging.debug('q %s, correct answer' % q.ordinal)
        return True

    def verify_person_attribute(self, netid, attribute, value):
        """
        Verify that the given attribute (eg birthdate) matches the value for the netid.

        Rather than chase all of the person identifier urls client-side, irws will return the
        list of identifiers. For birthdate, IRWS has the added value of discarding silly
        birthdates and matching on partial birthdates.
        """
        netid = self._clean(netid)
        attribute = self._clean(attribute)
        value = self._clean(value)

        dao = IRWS_DAO(self._conf)
        url = "/%s/v2/person?uwnetid=%s&%s=%s" % (self._service_name, netid, attribute, value)
        return dao.getURL(url, {'Accept': 'application/json'}).status == 200

    def _uwhr_person_from_json(self, data):
        """
        Internal method, for creating the UWhrPerson object.
        """
        person_data = json.loads(data)['person'][0]
        person = UWhrPerson()
        person.validid = person_data['validid']
        person.regid = person_data['regid']
        if 'studentid' in person_data:
            person.studentid = person_data['studentid']
        if 'birthdate' in person_data:
            person.birthdate = person_data['birthdate']

        if 'fname' in person_data:
            person.fname = person_data['fname']
        if 'lname' in person_data:
            person.lname = person_data['lname']

        if 'emp_ecs_code' in person_data:
            person.emp_ecs_code = person_data['emp_ecs_code']
        if 'emp_status_code' in person_data:
            person.emp_status_code = person_data['emp_status_code']
        if 'workday_last_active' in person_data:
            person.workday_last_active = person_data['workday_last_active']
        if 'workday_emp_status' in person_data:
            person.workday_emp_status = person_data['workday_emp_status']
        if 'workday_con_status' in person_data:
            person.workday_con_status = person_data['workday_con_status']
        if 'workday_aff_status' in person_data:
            person.workday_aff_status = person_data['workday_aff_status']
        person.source_code = person_data['source_code']
        person.source_name = person_data['source_name']
        person.status_code = person_data['status_code']
        person.status_name = person_data['status_name']
        if 'contact_email' in person_data:
            person.contact_email = person_data['contact_email']
        if 'workday_home_email' in person_data:
            person.workday_home_email = person_data['workday_home_email']
        if 'org_supervisor' in person_data:
            person.org_supervisor = person_data['org_supervisor']

        if 'pac' in person_data:
            person.pac = person_data['pac']
        if 'in_feed' in person_data:
            person.in_feed = person_data['in_feed']

        if 'wp_name' in person_data:
            wpn = person_data['wp_name'].split('|')
            person.wp_name = wpn[0]
            if len(wpn) > 1:
                person.wp_lname = wpn[1]
            if len(wpn) > 2:
                person.wp_fname = wpn[2]
        else:
            person.wp_name = person.fname + ' ' + person.lname
            person.wp_lname = person.lname
            person.wp_fname = person.fname

        if 'wp_publish' in person_data:
            person.wp_publish = person_data['wp_publish']
        else:
            person.wp_publish = 'Y'
        person.wp_phone = person_data.get('wp_phone', [])
        person.mailstop = person_data.get('mailstop', '')
        person.wp_address = person_data.get('wp_address', [])
        person.wp_title = person_data.get('wp_title', [])
        person.wp_department = person_data.get('wp_department', [])
        person.wp_email = person_data.get('wp_email', [])
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
        if 'birthdate' in person_data:
            person.birthdate = person_data['birthdate']

        person.fname = person_data['fname']
        person.lname = person_data['lname']

        person.categories = person_data['categories']
        person.source_code = person_data['source_code']
        person.source_name = person_data['source_name']
        person.status_code = person_data['status_code']
        person.status_name = person_data['status_name']

        if 'pac' in person_data:
            person.pac = person_data['pac']
        if 'in_feed' in person_data:
            person.in_feed = person_data['in_feed']
        if 'cnet_id' in person_data:
            person.cnet_id = person_data['cnet_id']
        if 'cnet_user' in person_data:
            person.cnet_user = person_data['cnet_user']
        person.wp_publish = person_data.get('wp_publish', 'Y')
        person.wp_phone = person_data.get('wp_phone', [])
        person.wp_title = person_data.get('wp_title', [])
        person.branch = person_data.get('branch', '')
        person.college = person_data.get('college', '')
        person.wp_department = person_data.get('wp_department', [])
        person.wp_email = person_data.get('wp_email', [])
        return person

    def _cascadia_person_from_json(self, data):
        """
        Internal method, for creating the CascadiaPerson object.
        """
        person_data = json.loads(data)['person'][0]
        person = CascadiaPerson()
        person.validid = person_data['validid']
        person.regid = person_data['regid']
        person.lname = person_data['lname']
        person.categories = person_data['categories']
        if 'birthdate' in person_data:
            person.birthdate = person_data['birthdate']
        if 'department' in person_data:
            person.department = person_data['department']
        if 'in_feed' in person_data:
            person.in_feed = person_data['in_feed']
        person.status_code = person_data.get('status_code', person.__class__.status_code)
        return person

    def _scca_person_from_json(self, data):
        """
        Internal method, for creating the SccaPerson object.
        """
        person_data = json.loads(data)['person'][0]
        person = SccaPerson()
        person.validid = person_data['validid']
        person.regid = person_data['regid']
        person.lname = person_data['lname']
        person.categories = person_data['categories']
        if 'birthdate' in person_data:
            person.birthdate = person_data['birthdate']
        if 'scca_company' in person_data:
            person.scca_company = person_data['scca_company']
        if 'scca_cca_eppn' in person_data:
            person.scca_cca_eppn = person_data['scca_cca_eppn']
        if 'scca_fhc_eppn' in person_data:
            person.scca_fhc_eppn = person_data['scca_fhc_eppn']
        if 'in_feed' in person_data:
            person.in_feed = person_data['in_feed']
        person.status_code = person_data.get('status_code', person.__class__.status_code)
        return person

    def _supplemental_person_from_json(self, data):
        """
        Internal method, for creating the SupplementalPerson object.
        """
        person_data = json.loads(data)['person'][0]
        person = SupplementalPerson()
        person.validid = person_data['validid']
        person.regid = person_data['regid']
        person.lname = person_data['lname']

        person.categories = person_data['categories']
        person.source_code = person_data['source_code']
        person.source_name = person_data['source_name']
        person.status_code = person_data['status_code']
        person.status_name = person_data['status_name']
        if 'comment_code' in person_data:
            person.comment_code = person_data['comment_code']
        if 'comment_name' in person_data:
            person.comment_name = person_data['comment_name']
        if 'college' in person_data:
            person.college = person_data['college']

        if 'in_feed' in person_data:
            person.in_feed = person_data['in_feed']

        person.id_proofing = person_data.get('id_proofing', {})
        person.contact_email = person_data.get('contact_email', [])

        return person

    def _person_from_json(self, data):
        persj = json.loads(data)['person'][0]
        idj = persj['identity']
        person = Person()
        person.regid = idj['regid']
        if 'lname' in idj:
            person.lname = idj['lname']
        if 'fname' in idj:
            person.fname = idj['fname']
        if 'identifiers' in idj:
            person.identifiers = copy.deepcopy(idj['identifiers'])
        return person

    def _regid_from_json(self, data):
        rj = json.loads(data)['regid'][0]
        regid = Regid()
        regid.regid = rj['regid']
        regid.entity_code = rj['entity_code']
        regid.entity_name = rj['entity_name']
        regid.status_code = rj['status_code']
        regid.status_name = rj['status_name']
        return regid

    def _pw_recover_from_json(self, data):
        info = json.loads(data)['profile'][0]
        ret = Profile()
        if 'validid' in info:
            ret.validid = info['validid']
        if 'recover_contacts' in info:
            ret.recover_contacts = info['recover_contacts']
        if 'recover_block_reasons' in info:
            ret.recover_block_reasons = info['recover_block_reasons']
        return ret

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
        subscription.subscription_data = sub_data.get('subscription_data', None)
        return subscription

    def _pdsentry_from_json(self, data):
        """
            Internal method, for creating the PDSEntry object.
            """
        person_data = json.loads(data)['pdsentry'][0]['entry']
        person = PDSEntry()
        person.regid = person_data.get('uwRegID', '')
        person.objectclass = person_data.get('objectClass', [])
        person.test = person_data.get('uwTest', '')
        person.eid = person_data.get('uwEmployeeID', '')
        person.ewpname = person_data.get('uwEWPName', '')
        person.ewpdept = person_data.get('uwEWPDept', [])
        person.ewpemail = person_data.get('uwEWPEmail', [])
        person.ewpphone = person_data.get('uwEWPPhone', [])
        person.ewptitle = person_data.get('uwEWPTitle', [])
        person.ewpaddr = person_data.get('uwEWPAddr', [])
        person.ewppublish = person_data.get('uwEWPPublish', '')
        person.employeehomedept = person_data.get('uwEmployeeHomeDepartment', '')
        person.employeemailstop = person_data.get('uwEmployeeMailstop', '')
        person.studentsystemkey = person_data.get('uwStudentSystemKey', '')
        person.sid = person_data.get('uwStudentID', '')
        person.swpname = person_data.get('uwSWPName', '')
        person.swpdept = person_data.get('uwSWPDept', [])
        person.swpemail = person_data.get('uwSWPEmail', '')
        person.swpclass = person_data.get('uwSWPClass', '')
        person.swppublish = person_data.get('uwSWPPublish', '')
        person.developmentid = person_data.get('uwDevelopmentID', '')
        person.wppublish = person_data.get('uwWPPublish', '')
        person.displayname = person_data.get('displayName', '')
        person.registeredname = person_data.get('uwPersonRegisteredName', '')
        person.registeredfirstmiddle = person_data.get('uwPersonRegisteredFirstMiddle', '')
        person.registeredsurname = person_data.get('uwPersonRegisteredSurname', '')
        person.cn = person_data.get('cn', '')
        person.sn = person_data.get('sn', '')
        person.preferredname = person_data.get('uwPersonPreferredName', '')
        person.preferredfirst = person_data.get('uwPersonPreferredFirst', '')
        person.preferredsurname = person_data.get('uwPersonPreferredSurname', '')
        person.uwnetid = person_data.get('uwNetID', '')
        person.uidnumber = person_data.get('uidNumber', '')
        person.edupersonaffiliation = person_data.get('eduPersonAffiliation', '')
        return person

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
        if 'formal_cname' in nd:
            name.formal_cname = nd['formal_cname']
        if 'formal_fname' in nd:
            name.formal_fname = nd['formal_fname']
        if 'formal_sname' in nd:
            name.formal_lname = nd['formal_sname']
        if 'formal_privacy' in nd:
            name.formal_privacy = nd['formal_privacy']
        if 'display_cname' in nd:
            name.display_cname = nd['display_cname']
        if 'display_fname' in nd:
            name.display_fname = nd['display_fname']
        if 'display_mname' in nd:
            name.display_mname = nd['display_mname']
        if 'display_sname' in nd:
            name.display_lname = nd['display_sname']
        if 'display_privacy' in nd:
            name.display_privacy = nd['display_privacy']
        return name

    def _qna_from_json(self, data):
        q_list = json.loads(data)['qna']
        ret = []
        for q in q_list:
            qna = QnA()
            qna.uwnetid = q['uwnetid']
            qna.ordinal = q['ordinal']
            qna.question = q['question']
            # qna.answer = q['answer']
            ret.append(qna)
        return ret

    def _generic_person_from_json(self, data):
        """
        Internal method to create a GenericPerson object.
        """
        person_data = json.loads(data)['person'][0]
        person = GenericPerson()
        attributes = [attribute for attribute in dir(GenericPerson) if not attribute.startswith('_')]
        for attribute in attributes:
            # set the attribute to the value in person_data, or if not set there,
            # the default attribute value
            setattr(person, attribute, person_data.get(attribute, getattr(GenericPerson, attribute)))
        return person
