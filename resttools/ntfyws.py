"""
This is the interface for interacting with the Notify Web Service.
"""
from resttools.dao import NTFYWS_DAO
import json
import logging
logger = logging.getLogger(__name__)


class NTFYWS(object):

    def __init__(self, conf, actas=None):
        self._service_name = conf['SERVICE_NAME']
        self.dao = NTFYWS_DAO(conf)

    def send_message(self, eppn, number, message, type='text'):
        """
        Sends a text (or voice) message to the phone number
        """
        if type == 'text':
            mtype = 'uw_direct_phone_sms'
            ts = 'Text'
        elif type == 'voice':
            mtype = 'uw_direct_phone_voice'
            ts = 'Say'
        else:
            return 400

        data = {'Dispatch': {
            'MessageType': mtype, 'Content': {
                'Recipient': eppn,
                'PhoneNumber': number,
                ts: message
                }
        }}

        url = "/%s/v1/dispatch" % (self._service_name)
        resp = self.dao.postURL(url, {"Content-Type": "application/json"}, json.dumps(data))

        return resp.status
