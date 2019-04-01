"""
This is the interface for interacting with the UW NetID Web Service.
"""
from . import rest
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


class NWS(rest.ConfDict, rest.Client):
    base_url = 'https://uwnetid.washington.edu/nws/v1'

    def get_netid_admins(self, netid):
        """
        Returns a list of NetidAdmin objects for the netid
        """
        url = "/uwnetid/%s/admin" % quote_plus(netid)
        response = self.get(url)

        if response.status_code != 200:
            raise DataFailureException(url, response.status_code, response.content)

        return self._admins_from_json(response.json())

    def get_netid_pwinfo(self, netid):
        """
        Returns NetidPwINfo object for the netid
        """
        url = "/uwnetid/%s/password" % quote_plus(netid)
        response = self.get(url)

        if response.status_code != 200:
            raise DataFailureException(url, response.status_code, response.content)

        return self._pwinfo_from_json(response.json())

    def set_netid_pw(self, netid, password, auth, action=None):
        """
        Sets password for netid
        """

        if action is None:
            action = self._pw_action

        url = "/uwnetid/%s/password" % quote_plus(netid)
        data = {'action': action, 'newPassword': password, 'uwNetID': netid, 'authMethod': auth}
        response = self.post(url, json=data)

        if response.status_code >= 500:
            raise DataFailureException(url, response.status_code, response.content)
        obj = response.json()
        if 'result' not in obj:
            # probably a mock data issue
            return (500, "Unable to set password.")
        return (obj['result'], obj['message'])

    def _admins_from_json(self, data):
        admins = [UWNetIdAdmin(name=admin.get('name', ''),
                               role=admin.get('role', ''),
                               type=admin.get('type', ''))
                  for admin in data.get('adminList', [])]
        return admins

    def _pwinfo_from_json(self, data):
        if 'minimumLength' in data:
            return UWNetIdPwInfo(min_len=data.get('minimumLength'),
                                 last_change=data.get('lastChange'),
                                 kerb_status=data.get('kerbStatus'))
        else:
            return None
