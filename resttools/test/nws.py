import json
from nose.tools import *
from mock import patch

from resttools.nws import NWS

import resttools.test.test_settings as settings
import logging.config
logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger(__name__)


class NWS_Test():

    def __init__(self):
        self.nws = NWS(settings.NWS_CONF)

    def test_get_netid_admins(self):
        admins = self.nws.get_netid_admins('groups')
        eq_(len(admins), 3)
        for a in admins:
            ok_((a.name == 'fox' and a.type == 'netid') or
                (a.name == 'dors' and a.type == 'netid') or
                (a.name == 'u_fox_browser6' and a.type == 'group'))

    def test_get_netid_admins_no_list(self):
        with patch('resttools.nws.NWS_DAO') as nws_dao:
            mock_response = nws_dao.return_value.getURL.return_value
            mock_response.status = 200
            mock_response.data = json.dumps({"timeStamp": "now", "uwNetID": "joe"})
            nws = NWS(settings.NWS_CONF)
            eq_(nws.get_netid_admins('joe'), [])

    def test_get_netid_pw(self):
        pw = self.nws.get_netid_pwinfo('groups')
        eq_(pw.min_len, 8)
        eq_(pw.kerb_status, 'Active')

    def test_pwinfo_from_json(self):
        pw = self.nws._pwinfo_from_json(json.dumps({'minimumLength': 50000}))
        eq_(pw.__dict__, {'min_len': 50000, 'kerb_status': 'Active', 'last_change': ''})

        pw = self.nws._pwinfo_from_json(json.dumps(
                                        {'minimumLength': 4000, 'lastChange': 'tomorrow', 'kerbStatus': 'dissed'}))
        eq_(pw.__dict__, {'min_len': 4000, 'kerb_status': 'dissed', 'last_change': 'tomorrow'})

        pw = self.nws._pwinfo_from_json(json.dumps({}))
        eq_(pw, None)
