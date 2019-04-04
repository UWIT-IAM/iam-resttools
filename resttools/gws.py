"""
This is the interface for interacting with the Group Web Service.
"""
from . import rest
import urllib.parse
import requests
from operator import itemgetter
from functools import partial
quote = partial(urllib.parse.quote, safe=',')


class GroupsClient(rest.Client):
    base_url = 'https://groups.uw.edu/group_sws/v3'
    raise_for_status = True

    def get_members(self, groupid, effective=False, mapfunc=itemgetter('id')):
        groupid = quote(groupid)
        url = f'/group/{groupid}/member'
        if effective:
            url = f'/group/{groupid}/effective_member'
        members = self.get(url).json()['data']
        if mapfunc:
            members = map(mapfunc, members)
        members = filter(None, members)
        return list(members)

    def is_member(self, groupid, userid, effective=False):
        groupid = quote(groupid)
        userid = quote(userid)
        url = f'/group/{groupid}/member/{groupid}'
        if effective:
            url = f'/group/{groupid}/effective_member/{groupid}'
        try:
            self.get(url)
            return True
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                return False
            raise  # re-raise if anything other than 404

    def put_members(self, groupid, *members):
        groupid = quote(groupid)
        members = quote(','.join(members))
        return self.put(f'/group/{quote(groupid)}/member/{members}').json()

    def delete_members(self, groupid, *members):
        groupid = quote(groupid)
        members = quote(','.join(members))
        self.put(f'/group/{quote(groupid)}/member/{members}').json()
