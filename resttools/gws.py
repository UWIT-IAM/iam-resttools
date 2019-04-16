"""
This is the interface for interacting with the Group Web Service.
"""
from . import rest
import urllib.parse
import requests
from operator import itemgetter
from functools import partial
quote = partial(urllib.parse.quote, safe=',')

CLIENT = rest.Client()
CLIENT.base_url = 'https://groups.uw.edu/group_sws/v3'
CLIENT.raise_for_status = True


def get_members(groupid, effective=False, convert=itemgetter('id')):
    groupid = quote(groupid)
    url = f'/group/{groupid}/member'
    if effective:
        url = f'/group/{groupid}/effective_member'
    members = CLIENT.get(url).json()['data']
    if convert:
        members = map(convert, members)
        members = list(filter(None, members))  # remove empties
    return members


def is_member(groupid, userid, effective=False):
    groupid = quote(groupid)
    userid = quote(userid)
    url = f'/group/{groupid}/member/{groupid}'
    if effective:
        url = f'/group/{groupid}/effective_member/{groupid}'
    try:
        CLIENT.get(url)
        return True
    except requests.HTTPError as e:
        if e.response.status_code == 404:
            return False
        raise  # re-raise if anything other than 404


def put_members(groupid, *members):
    groupid = quote(groupid)
    members = quote(','.join(members))
    return CLIENT.put(f'/group/{quote(groupid)}/member/{members}').json()


def delete_members(groupid, *members):
    groupid = quote(groupid)
    members = quote(','.join(members))
    CLIENT.put(f'/group/{quote(groupid)}/member/{members}').json()
