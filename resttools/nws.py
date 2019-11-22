"""
This is the interface for interacting with the UW NetID Web Service.
"""
from resttools.dao import NWS_DAO
from resttools.models.nws import UWNetIdAdmin, UWNetIdPwInfo
from resttools.exceptions import DataFailureException
from six.moves.urllib.parse import quote_plus
import json
import logging
logger = logging.getLogger(__name__)

# note.  Some messages from nws set pw
# 409, "That's not a good password because you used that password in the not too distant past."
# 409, "That's not a good password because it is your username."
# 409, "That's not a good password because it does not contain enough different character classes
#       (uppercase, lowercase, digits, punctuation)."
# 409, "That's not a good password because it needs more complex capitalization."
#


class NWS(object):

    def __init__(self, conf, actas=None):
        service_name = conf['SERVICE_NAME']
        version = conf.get('VERSION', 'v1')
        self._base_url = '/{}/{}'.format(service_name, version)
        self._pw_action = 'Set'
        if 'PASSWORD_ACTION' in conf:
            self._pw_action = conf['PASSWORD_ACTION']
        self.dao = NWS_DAO(conf)

    def get_netid_admins(self, netid):
        """
        Returns a list of NetidAdmin objects for the netid
        """
        url = "%s/uwnetid/%s/admin" % (self._base_url, quote_plus(netid))
        response = self.dao.getURL(url, self._headers({"Accept": "application/json"}))

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        return self._admins_from_json(response.data)

    def get_netid_pwinfo(self, netid):
        """
        Returns NetidPwINfo object for the netid
        """
        url = "%s/uwnetid/%s/password" % (self._base_url, quote_plus(netid))
        response = self.dao.getURL(url, self._headers({"Accept": "application/json"}))

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        return self._pwinfo_from_json(response.data)

    def get_netid_supported(self, netid):
        """
        Returns a list of Supportees for the netid
        """
        url = "%s/uwnetid/%s/supported" % (self._base_url, quote_plus(netid))
        response = self.dao.getURL(url, self._headers({"Accept": "application/json"}))

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        return self._supportees_from_json(response.data)

    def set_netid_pw(self, netid, password, auth, action=None):
        """
        Sets password for netid
        """

        if action is None:
            action = self._pw_action

        url = "%s/uwnetid/%s/password" % (self._base_url, quote_plus(netid))
        data = {'action': action, 'newPassword': password, 'uwNetID': netid, 'authMethod': auth}
        response = self.dao.postURL(url, {"Content-type": "application/json"}, json.dumps(data))

        if response.status >= 500:
            raise DataFailureException(url, response.status, response.data)
        obj = json.loads(response.data)
        if 'result' not in obj:
            # probably a mock data issue
            return (500, "Unable to set password.")
        return (obj['result'], obj['message'])

    def _admins_from_json(self, data):
        adminobj = json.loads(data)
        admins = [UWNetIdAdmin(name=admin.get('name', ''),
                               role=admin.get('role', ''),
                               type=admin.get('type', ''))
                  for admin in adminobj.get('adminList', [])]
        return admins

    def _pwinfo_from_json(self, data):
        infoobj = json.loads(data)
        if 'minimumLength' in infoobj:
            return UWNetIdPwInfo(min_len=infoobj.get('minimumLength', None),
                                 last_change=infoobj.get('lastChange', None),
                                 kerb_status=infoobj.get('kerbStatus', None))
        else:
            return None

    def _supportees_from_json(self, data):
        supportobj = json.loads(data)
        supportees = supportobj.get('supportedList', [])
        return supportees

    def _headers(self, headers):
        # could auto-add headers here
        return headers

    def _add_header(self, headers, header, value):
        if not headers:
            return {header: value}

        headers[header] = value
        return headers
