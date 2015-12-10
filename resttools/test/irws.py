import json
import logging
from nose.tools import *

from resttools.irws import IRWS

import resttools.test.test_settings as settings
import logging.config
logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger(__name__)


class IRWS_Test():

    def __init__(self):
        self.irws = IRWS(settings.IRWS_CONF)

    def test_get_name_by_netid(self):
        name = self.irws.get_name_by_netid('javerage')
        eq_(name.display_cname, 'JAMES AVERAGE STUDENT')
        eq_(name.display_privacy, 'Public')

    def test_get_uwnetid_by_regid(self):
        netid = self.irws.get_uwnetid(regid='DC5C0C166A7C11D5A4AE0004AC494FFE', status=30)
        eq_(netid.uwnetid, 'lucy123wf')
        eq_(netid.uid, '2024')
        netids = self.irws.get_uwnetid(regid='DC5C0C166A7C11D5A4AE0004AC494FFE', status=30, ret_array=True)
        eq_(len(netids), 2)
        eq_(netids[1].uwnetid, 'junk4')

    def test_get_uwnetid_by_eid(self):
        netid = self.irws.get_uwnetid(eid='003433412', source=1, status=30)
        eq_(netid.uwnetid, 'fox')
        eq_(netid.uid, '994010')

    def test_get_person_by_netid(self):
        person = self.irws.get_person(netid='wdspud867')
        eq_(person.lname, 'Daywork')
        eq_(person.fname, 'Spud')
        eq_(person.identifiers['hepps'], '/person/hepps/867003233')

    def test_get_person_by_netid_nonexists(self):
        person = self.irws.get_person(netid='pud867')
        eq_(person, None)

    def test_get_uwhr_person_hepps(self):
        uwhr = self.irws.get_uwhr_person('123456789', source='hepps')
        eq_(uwhr.lname, 'STUDENT')

    def test_get_sdb_person(self):
        sdb = self.irws.get_sdb_person('000083856')
        eq_(sdb.lname, 'STUDENT')

    def test_get_supplemental_person(self):
        s = self.irws.get_supplemental_person('88E13ABD')
        eq_(s.lname, 'AVERAGE')

    def test_get_regid(self):
        r = self.irws.get_regid(netid='joeuser')
        eq_(r.entity_code, '10')
        eq_(r.status_code, '50')
        r = self.irws.get_regid(regid='FC8E9A4FD5A940ACAC6306EA7DC7D742')
        eq_(r.entity_code, '10')
        eq_(r.status_code, '50')

    def test_get_qna(self):
        qna = self.irws.get_qna('user1q')
        eq_(len(qna), 3)
        eq_(qna[0].ordinal, '1')
        eq_(qna[1].ordinal, '2')
        eq_(qna[2].ordinal, '3')

    def test_verify_qna(self):
        correct = {'1': 'skyblue', '2': 'mememe', '3': 'begood'}
        st = self.irws.get_verify_qna('user1q', correct)
        eq_(st, True)
        incorrect = {'1': 'skyblue', '2': 'NOTmememe', '3': 'begood'}
        st = self.irws.get_verify_qna('user1q', incorrect)
        eq_(st, False)

    def test_verify_person_attibute(self):
        st = self.irws.verify_person_attribute('javerage', 'birthdate', '2015-10-04')
        eq_(st, True)
        st = self.irws.verify_person_attribute('javerage', 'birthdate', '2015-10-03')
        eq_(st, False)

    def test_get_cascadia_person(self):
        g = self.irws.get_cascadia_person('960031000')
        eq_(g.lname, 'CASLAST')
        eq_(g.birthdate, '1981-01-01')
        eq_(g.department, 'STU')
        eq_(g.status_code, '3')

    def test_get_scca_person(self):
        g = self.irws.get_scca_person('FHSC40999')
        eq_(g.lname, 'CCALAST')
        eq_(g.scca_company, 'CCA')
        eq_(g.scca_cca_eppn, 'ccalast@seattlecca.org')
        eq_(g.status_code, '3')

    def test_get_generic_person(self):
        g = self.irws.get_generic_person('/person/generic/01234')
        eq_(g.lname, 'LEGACYEMAIL')
        eq_(g.contact_email, ['legacyemail@example.com'])
        eq_(g.source_code, '2')
        # not set in our payload, assert the default value
        eq_(g.status_code, '')

    def test_verify_sc_pin(self):
        st = self.irws.verify_sc_pin('user1s', '321abc')
        eq_(st, 404)
        st = self.irws.verify_sc_pin('user1s', '123456')
        eq_(st, 200)
        st = self.irws.verify_sc_pin('user1q', '123456')
        eq_(st, 404)
