# config for tests

import os

DEBUG = False

RUN_MODE = 'File'
MOCK_ROOT = os.path.abspath(os.path.dirname(__file__)) + '/test_data'

#

GWS_CONF = {
    'HOST':  'https://iam-ws.u.washington.edu:7443',
    'MAX_POOL_SIZE': 5,
}

IRWS_CONF = {
    'HOST':  'https://mango-dev.u.washington.edu:646',
    'SERVICE_NAME': 'registry-dev',
    'MAX_POOL_SIZE': 5,
    'VERIFY_HOST': False,
}

NWS_CONF = {
    'HOST':  'https://uwnetid.washington.edu',
    'SERVICE_NAME': 'nws',
    'MAX_POOL_SIZE': 5,
    'PASSWORD_ACTION': 'Test',
}

NTFYWS_CONF = {
    'HOST':  'https://notify-dev.s.uw.edu',
    # 'HOST':  'https://notify.uw.edu',
    'SERVICE_NAME': 'notification',
    'MOCK_ROOT': 'nsspr/mock_data',
}


# augment handlers' configs
for conf in (GWS_CONF, IRWS_CONF, NWS_CONF):
    if 'RUN_MODE' not in conf:
        conf['RUN_MODE'] = RUN_MODE
    if 'MOCK_ROOT' not in conf:
        conf['MOCK_ROOT'] = MOCK_ROOT

LOGGING = {
    'version': 1,
    'formatters': {
        'plain': {
            'format': '%(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'stream': 'ext://sys.stdout',
            'formatter': 'plain',
        },
        'default': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'formatter': 'plain',
            'filename': 'tests.log',
        },
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['default'],
    },
    'suds': {
        'level': 'INFO',
        'handlers': ['default']
    },
}
