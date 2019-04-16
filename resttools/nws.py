"""
This is the interface for interacting with the UW NetID Web Service.
"""
from . import rest, gws
from resttools.models.nws import UWNetIdAdmin, UWNetIdPwInfo
from resttools.exceptions import DataFailureException
from urllib.parse import quote_plus, quote
import requests
import json
import logging
logger = logging.getLogger(__name__)


CLIENT = rest.Client()
CLIENT.base_url = 'https://uwnetid.washington.edu/nws/v1'
CLIENT.raise_for_status = True


def get_admins(netid):
    response = CLIENT.get(f'/uwnetid/{quote(netid)}/admin')
    groups = []
    for admin in response.json().get('adminList', []):
        if admin.get('type') == 'netid':
            yield admin.get('name')
        elif admin.get('type') == 'group':
            groups.append(admin.get('name'))
        else:
            value = '='.join([admin.get('type'), admin.get('name')])
            logger.warning(f'unrecognized admin type/value discarded ({value})')
    for group in groups:
        yield from gws.get_members(group, effective=True)


def get_password_info(netid):
    response = CLIENT.get(f'/uwnetid/{quote(netid)}/password')


def reset_password(netid, password, is_test=False, auth_method='unspecified'):
    if not netid or not password:
        raise ValueError('no netid/password')
    data = dict(newPassword=password, authMethod=auth_method, uwNetID=netid)
    if is_test:
        data['action'] = 'Test'
    try:
        response = client.post(f'/uwnetid/{quote(netid)}/password', json=data)
    except requests.HTTPError as e:
        if e.response.status_code == 409:
            msg = e.response.json().get('message')
            mode = 'Test' if is_test else 'Set'
            logger.info(f'Bad password for {mode}: netid={netid}, msg={msg}')
            raise ValueError(message)
        raise
    return response.json()

class NWS(rest.ConfDict, rest.Client):
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
