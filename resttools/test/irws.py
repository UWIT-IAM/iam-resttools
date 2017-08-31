import json
from nose.tools import *
from resttools.irws import IRWS
from resttools.exceptions import (InvalidIRWSName, DataFailureException,
                                  BadInput, ResourceNotFound)
from resttools.models.irws import SdbPerson
import resttools.test.test_settings as settings
import logging.config
logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger(__name__)


class IRWS_Test():

    def __init__(self):
        self.irws = IRWS(settings.IRWS_CONF)

    def test_get_name_by_netid(self):
        name = self.irws.get_name_by_netid('javerage')
        eq_(name.preferred_cname, 'JAMES AVERAGE STUDENT-P')
        eq_(name.preferred_privacy, 'Public')

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

    def test_post_hr_person_by_netid(self):
        uwhr = self.irws.post_hr_person_by_netid('javerage', wp_publish='E')
        eq_(uwhr.wp_publish, 'E')

    def test_post_hr_person_bad_publish_value(self):
        assert_raises(BadInput,
                      self.irws.post_hr_person_by_netid,
                      'javerage', wp_publish='X')

    def test_post_hr_person_not_employee(self):
        assert_raises(ResourceNotFound,
                      self.irws.post_hr_person_by_netid,
                      'notaperson', wp_publish='Y')

    def test_get_uwhr_person_hepps(self):
        uwhr = self.irws.get_uwhr_person('123456789', source='hepps')
        eq_(uwhr.lname, 'STUDENT')

    def test_get_sdb_person(self):
        sdb = self.irws.get_sdb_person('000083856')
        eq_(sdb.lname, 'STUDENT')

    def test_get_sdb_person_default_wp_publish(self):
        data = dict(
            validid='123', regid='000', studentid='111', fname='F', lname='L',
            categories=[], source_code='1', source_name='N', status_code='2',
            status_name='M')
        sdb = SdbPerson(**data)
        eq_(sdb.wp_publish_options, None)
        eq_(sdb.validid, '123')

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
        correct = ['skyblue', 'mememe', 'begood']
        incorrect = ['skyblue', 'NOTmememe', 'begood']
        eq_(self.irws.get_verify_qna('user1q', correct), True)
        eq_(self.irws.get_verify_qna('user1q', incorrect), False)
        eq_(self.irws.get_verify_qna('user1q', correct[:2]), False)

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

    def test_put_name_by_netid(self):
        # prime the cache first
        # irws.get_name_by_netid('javerage')

        response = self.irws.put_name_by_netid(
            'javerage', first='J', middle='', last='Student')
        eq_(200, response)
        name = self.irws.get_name_by_netid('javerage')
        eq_('J', name.preferred_fname)
        eq_('', name.preferred_mname)
        eq_('Student', name.preferred_lname)

    def test_put_name_by_netid_no_user(self):
        assert_raises(DataFailureException,
                      self.irws.put_name_by_netid,
                      'nonuser',
                      first='J', middle='', last='Student')

    def test_valid_name_part_good(self):
        ok_(self.irws._valid_name_part('james'))
        ok_(self.irws._valid_name_part(' '))
        ok_(self.irws._valid_name_part(' !$&\'*-,.?^_`{}~#+%'))

    def test_valid_name_part_bad(self):
        bad_chars = '"():;<>[\]|@'
        assert not self.irws._valid_name_part(u'Jos\xe9')  # utf-8
        for c in bad_chars:
            assert not self.irws._valid_name_part(c)

    def test_valid_name_part_too_long(self):
        # 64 is the magic number
        bad_name = 'a' * 65
        assert not self.irws._valid_name_part(bad_name)
        # one less should be good
        assert self.irws._valid_name_part(bad_name[:-1])

    def test_valid_name_json_good(self):
        names = json.loads(
            self.irws.valid_name_json(first='joe', middle='average', last='user'))
        name = names['name'][0]
        eq_(name['preferred_fname'], 'joe')
        eq_(name['preferred_mname'], 'average')
        eq_(name['preferred_sname'], 'user')

    def test_valid_irws_name_empty_middle_name(self):
        names = json.loads(self.irws.valid_name_json(first='joe', middle='', last='user'))
        eq_(names['name'][0]['preferred_mname'], '')

    def test_valid_name_json_required_fields_missing(self):
        bad_data_list = [
            dict(first='', middle='average', last='user'),
            dict(first='joe', middle='average', last='')]

        for bad_data in bad_data_list:
            assert_raises(InvalidIRWSName,
                          self.irws.valid_name_json,
                          **bad_data)

    def test_valid_irws_name_bad_characters(self):
        bad_data_list = [
            ('@', 'average', 'user'),
            ('joe', '@', 'user'),
            ('joe', 'average', '@'),
            ]

        for bad_data in bad_data_list:
            bad_name = dict(first=bad_data[0], middle=bad_data[1], last=bad_data[2])
            assert_raises(InvalidIRWSName,
                          self.irws.valid_name_json,
                          **bad_name)

    def test_valid_irws_name_too_long(self):
        # 80 is the magic number
        bad_data_list = [
            ('f' * 30, 'm' * 30, 'l' * 19),
            ('f' * 40, '', 'l' * 40)]

        for bad_data in bad_data_list:
            # one less character will pass
            good_name = (bad_data[0:2] + (bad_data[2][:-1],))
            ok_(self.irws.valid_name_json(first=good_name[0],
                                          middle=good_name[1], last=good_name[2]))
            # failure
            assert_raises(InvalidIRWSName,
                          self.irws.valid_name_json,
                          first=bad_data[0], middle=bad_data[1], last=bad_data[2])
