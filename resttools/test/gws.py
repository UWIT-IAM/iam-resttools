import json
import logging
from nose.tools import *

from resttools.gws import GWS
from resttools.exceptions import DataFailureException

import resttools.test.test_settings as settings
import logging.config
logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger(__name__)


class GWS_Test():

    def __init__(self):
        self.gws = GWS(settings.GWS_CONF)

    def test_search_groups(self):
        groups = self.gws.search_groups(name='2015spr-phys*1', stem='course')
        eq_(len(groups), 199)
        groups = self.gws.search_groups(member='javerage')
        eq_(len(groups), 24)

    def test_get_group(self):
        group = self.gws.get_group_by_id('course_2015spr-phys114a')
        eq_(group.name, 'course_2015spr-phys114a')

    @raises(DataFailureException)
    def test_get_group_members_403(self):
        members = self.gws.get_members('course_2015spr-phys114a')
