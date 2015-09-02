import json
import logging
from nose.tools import *

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
            ok_(a.name == 'fox' or a.name == 'dors' or a.name == 'spud123')

    def test_get_netid_pw(self):
        pw = self.nws.get_netid_pwinfo('groups')
        eq_(pw.min_len, 8)
