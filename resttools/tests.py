# various nose tests

from nose.tools import *

import resttools.test.test_settings as settings

import logging.config
logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger('root')

from resttools.test.irws import IRWS_Test
