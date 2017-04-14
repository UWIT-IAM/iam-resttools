"""
This is the interface for interacting with the Group Web Service.
"""
from resttools.dao import GWS_DAO
from resttools.exceptions import InvalidGroupID
from resttools.exceptions import DataFailureException
from resttools.models.gws import Group, CourseGroup, GroupReference
from resttools.models.gws import GroupUser, GroupMember
from six.moves.urllib.parse import urlencode
from lxml import etree
import re
from jinja2 import Environment, PackageLoader

import logging
logger = logging.getLogger(__name__)


class GWS(object):
    """
    The GWS object has methods for getting group information.
    """
    def __init__(self, conf, actas=None):
        self._service_name = 'gws'
        self._conf = conf
        self._j2env = Environment(loader=PackageLoader('resttools',
                                                       'templates/gws'))
        self._actas = actas
        self.dao = GWS_DAO(conf)

    QTRS = {'win': 'winter', 'spr': 'spring', 'sum': 'summer', 'aut': 'autumn'}

    def search_groups(self, **kwargs):
        """
        Returns a list of resttools.GroupReference objects matching the
        passed parameters. Valid parameters are:
            name: parts_of_name
                name may include the wild-card (*) character.
            stem: group_stem
            member: member netid
            owner: admin netid
            instructor: instructor netid
                stem="course" will be set when this parameter is passed.
            student: student netid
                stem="course" will be set when this parameter is passed.
            affiliate: affiliate_name
            type: search_type
                Values are 'direct' to search for direct membership and
                'effective' to search for effective memberships. Default is
                direct membership.
            scope: search_scope
                Values are 'one' to limit results to one level of stem name
                and 'all' to return all groups.
        """
        kwargs = dict((k.lower(), v.lower()) for k, v in kwargs.items())
        if 'type' in kwargs and (kwargs['type'] != 'direct' and
                                 kwargs['type'] != 'effective'):
            del(kwargs['type'])

        if 'scope' in kwargs and (kwargs['scope'] != 'one' and
                                  kwargs['scope'] != 'all'):
            del(kwargs['scope'])

        if "instructor" in kwargs or "student" in kwargs:
            kwargs["stem"] = "course"

        url = "/group_sws/v2/search?" + urlencode(kwargs)
        response = self.dao.getURL(url, self._headers({"Accept": "text/xml"}))

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        groups = []
        root = etree.fromstring(response.data)
        e_grs_list = root.find('groupreferences').findall('groupreference')
        for e in e_grs_list:
            group = GroupReference()
            group.uwregid = e.find('regid').text
            group.title = e.find('title').text
            group.description = e.find('description').text
            group.name = e.find('name').text
            groups.append(group)

        return groups

    def get_group_by_id(self, group_id):
        """
        Returns a resttools.Group object for the group identified by the
        passed group ID.
        """
        if not self._is_valid_group_id(group_id):
            raise InvalidGroupID(group_id)

        url = "/group_sws/v2/group/%s" % group_id
        response = self.dao.getURL(url, self._headers({"Accept": "text/xml"}))

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        return self._group_from_xml(response.data)

    def create_group(self, group):
        """
        Creates a group from the passed resttools.Group object.
        """
        body = self._xml_from_group(group)

        url = "/group_sws/v2/group/%s" % group.name
        response = self.dao.putURL(
            url, self._headers({"Accept": "text/xml", "Content-Type": "text/xml"}),
            body)

        if response.status != 201:
            raise DataFailureException(url, response.status, response.data)

        return self._group_from_xml(response.data)

    def put_group(self, group):
        """
        Updates a group from the passed resttools.Group object.
        """
        body = self._xml_from_group(group)

        url = "/group_sws/v2/group/%s" % group.name
        response = self.dao.putURL(
            url, self._headers({"Accept": "text/xml",
                                "Content-Type": "text/xml", "If-Match": "*"}),
            body)

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        return self._group_from_xml(response.data)

    def delete_group(self, group_id):
        """
        Deletes the group identified by the passed group ID.
        """
        if not self._is_valid_group_id(group_id):
            raise InvalidGroupID(group_id)

        url = "/group_sws/v2/group/%s" % group_id
        response = self.dao.deleteURL(url, self._headers({}))

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        return True

    def get_members(self, group_id):
        """
        Returns a list of resttools.GroupMember objects for the group
        identified by the passed group ID.
        """
        if not self._is_valid_group_id(group_id):
            raise InvalidGroupID(group_id)

        url = "/group_sws/v2/group/%s/member" % group_id
        response = self.dao.getURL(url, self._headers({"Accept": "text/xml"}))

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        return self._members_from_xml(response.data)

    def put_membership(self, group_id, members):
        """
        Puts the membership of the group represented by the passed group id.
        Members is an object: name=<member_id>, type=<member_type>
        Returns a list of members not found.
        """
        if not self._is_valid_group_id(group_id):
            raise InvalidGroupID(group_id)

        body = self._xml_from_members(group_id, members)

        url = "/group_sws/v2/group/%s/member" % group_id
        response = self.dao.putURL(
            url, self._headers({"Content-Type": "text/xml", "If-Match": "*"}),
            body)

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        return self._notfoundmembers_from_xml(response.data)

    def put_members(self, group_id, members):
        """
        Puts members into the group represented by the passed group id.
        Members is a list of string. (could be prefaced, e.g. 'u:user_id')
        Returns a list of members not found.
        """
        if not self._is_valid_group_id(group_id):
            raise InvalidGroupID(group_id)

        if len(members) == 0:
            return []

        url = "/group_sws/v2/group/%s/member/%s" % (group_id, ','.join(members))
        response = self.dao.putURL(
            url, self._headers({"Content-Type": "text/xml", "If-Match": "*"}),
            None)

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        return self._notfoundmembers_from_xml(response.data)

    def delete_members(self, group_id, members):
        """
        Delete members from the group represented by the passed group id.
        Members is a list of string.
        Returns a list of members not found.
        """
        if not self._is_valid_group_id(group_id):
            raise InvalidGroupID(group_id)

        if len(members) == 0:
            return True

        url = "/group_sws/v2/group/%s/member/%s" % (group_id, ','.join(members))
        response = self.dao.deleteURL(url, self._headers(
            {"Content-Type": "text/xml", "If-Match": "*"}))

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        return True

    def get_effective_members(self, group_id):
        """
        Returns a list of effective resttools.GroupMember objects for the
        group identified by the passed group ID.
        """
        if not self._is_valid_group_id(group_id):
            raise InvalidGroupID(group_id)

        url = "/group_sws/v2/group/%s/effective_member" % group_id
        response = self.dao.getURL(url, self._headers({"Accept": "text/xml"}))

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        return self._members_from_xml(response.data)

    def get_effective_member_count(self, group_id):
        """
        Returns a count of effective members for the group identified by the
        passed group ID.
        """
        if not self._is_valid_group_id(group_id):
            raise InvalidGroupID(group_id)

        url = "/group_sws/v2/group/%s/effective_member?view=count" % group_id
        response = self.dao.getURL(url, self._headers({"Accept": "text/xml"}))

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        root = etree.fromstring(response.data)
        count = root.find('member_count').get("count")

        return int(count)

    def is_effective_member(self, group_id, netid):
        """
        Returns True if the netid is in the group, False otherwise.
        """
        if not self._is_valid_group_id(group_id):
            raise InvalidGroupID(group_id)

        # GWS doesn't accept EPPNs on effective member checks, for UW users
        netid = re.sub('@washington.edu', '', netid)

        url = "/group_sws/v2/group/%s/effective_member/%s" % (group_id, netid)
        response = self.dao.getURL(url, self._headers({"Accept": "text/xml"}))

        if response.status == 404:
            return False
        elif response.status == 200:
            return True
        else:
            raise DataFailureException(url, response.status, response.data)

    def _group_from_xml(self, data):
        root = etree.fromstring(data)
        gr = root.find('group')
        group_id = gr.find('name').text
        if re.match(r'^course_', group_id):
            group = CourseGroup()
            group.curriculum_abbr = gr.find('course_curr').text.upper()
            group.course_number = gr.find('course_no').text
            group.year = gr.find('course_year').text
            group.quarter = self.QTRS[gr.find('course_qtr').text]
            group.section_id = gr.find('course_sect').text.upper()
            group.sln = gr.find('course_sln').text

            group.instructors = []
            instructors = (gr.find('course_instructors').findall('course_instructor'))
            for instructor in instructors:
                group.instructors.append(GroupMember(name=instructor.text,
                                                     member_type="uwnetid"))
        else:
            group = Group()

        group.name = group_id
        group.uwregid = gr.find('regid').text
        group.title = gr.find('title').text
        group.description = gr.find('description').text
        group.contact = gr.find('contact').text
        group.authnfactor = gr.find('authnfactor').text
        group.classification = gr.find('classification').text
        group.emailenabled = gr.find('emailenabled').text
        group.dependson = gr.find('dependson').text
        group.publishemail = gr.find('publishemail').text

        try:
            group.reporttoorig = gr.find('reporttoorig').text
        except AttributeError:
            # Legacy class name for this attribute
            group.reporttoorig = gr.find('reporttoowner').text

        for user in gr.find('admins').findall('admin'):
            group.admins.append(GroupUser(user.text,
                                          user_type=user.get('type')))

        for user in gr.find('updaters').findall('updater'):
            group.updaters.append(GroupUser(name=user.text,
                                            user_type=user.get("type")))

        for user in gr.find('creators').findall('creator'):
            group.creators.append(GroupUser(name=user.text,
                                            user_type=user.get("type")))

        for user in gr.find('readers').findall('reader'):
            group.readers.append(GroupUser(name=user.text,
                                           user_type=user.get("type")))

        for user in gr.find('optins').findall('optin'):
            group.optins.append(GroupUser(name=user.text,
                                          user_type=user.get("type")))

        for user in gr.find('optouts').findall('optout'):
            group.optouts.append(GroupUser(name=user.text,
                                           user_type=user.get("type")))

        # viewers are not used according to Jim Fox
        # group.viewers = []
        # for user in gr.find('viewers').findall('viewer'):
        #     group.viewers.append(GroupUser(name=user.text,
        #                                    user_type=user.get("type")))
        return group

    def _xml_from_group(self, group):
        template = self._j2env.get_template("group.xml")
        return template.render({"group": group})

    def _members_from_xml(self, data):
        e_mbrs = etree.fromstring(data).find('group').find('members')
        e_mbr_list = e_mbrs.findall('member')

        members = []
        for member in e_mbr_list:
            members.append(GroupMember(name=member.text,
                                       member_type=member.get("type")))

        return members

    def _notfoundmembers_from_xml(self, data):
        members = []
        root = etree.fromstring(data)
        e_nf = root.find('notfoundmembers')
        if e_nf is None:
            return members
        e_nf_list = e_nf.findall('notfoundmember')
        for m in e_nf_list:
            members.append(m.text)

        return members

    def _xml_from_members(self, group_id, members):
        template = self._j2env.get_template("members.xml")
        return template.render({"group_id": group_id, "members": members})

    def _is_valid_group_id(self, group_id):
        if not re.match(r'^[a-z0-9][\w\.-]+$', group_id, re.I):
            return False

        return True

    def _headers(self, headers):
        if self._actas:
            headers = self._add_header(headers, "X-UW-Act-as", self._actas)

        return headers

    def _add_header(self, headers, header, value):
        if not headers:
            return {header: value}

        headers[header] = value
        return headers
