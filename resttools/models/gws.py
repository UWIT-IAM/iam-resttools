
class GroupReference():
    uwregid = ''
    name = ''
    title = ''
    description = ''
    url = ''

    def __str__(self):
        return "{uwregid: %s, name: %s, title: %s, description: %s}" % (
            self.uwregid, self.name, self.title, self.description)


class Group():
    CLASSIFICATION_NONE = "u"
    CLASSIFICATION_PUBLIC = "p"
    CLASSIFICATION_RESTRICTED = "r"
    CLASSIFICATION_CONFIDENTIAL = "c"

    CLASSIFICATION_TYPES = (
        (CLASSIFICATION_NONE, "Unclassified"),
        (CLASSIFICATION_PUBLIC, "Public"),
        (CLASSIFICATION_RESTRICTED, "Restricted"),
        (CLASSIFICATION_CONFIDENTIAL, "Confidential")
    )

    uwregid = ''

    name = ''
    title = ''
    description = ''
    contact = ''
    authnfactor = 1
    classification = ''
    emailenabled = ''
    dependson = ''
    publishemail = ''
    reporttoorig = ''

    def __init__(self, *args, **kwargs):
        self.admins = []
        self.creators = []
        self.optins = []
        self.optouts = []
        self.readers = []
        self.updaters = []

    def __str__(self):
        return "{uwregid: %s, name: %s, title: %s, description: %s}" % (
            self.uwregid, self.name, self.title, self.description)

    def has_regid(self):
        return self.uwregid is not None and len(self.uwregid) == 32


class CourseGroup(Group):
    SPRING = "spring"
    SUMMER = "summer"
    AUTUMN = "autumn"
    WINTER = "winter"

    QUARTERNAME_CHOICES = (
        (SPRING, "Spring"),
        (SUMMER, "Summer"),
        (AUTUMN, "Autumn"),
        (WINTER, "Winter"),
    )

    curriculum_abbr = ''
    course_number = ''
    year = 0
    quarter = ''
    section_id = ''
    sln = 0


class GroupUser():
    UWNETID_TYPE = "uwnetid"
    EPPN_TYPE = "eppn"
    GROUP_TYPE = "group"
    DNS_TYPE = "dns"
    NONE_TYPE = "none"

    TYPE_CHOICES = (
        (UWNETID_TYPE, "UWNetID"),
        (EPPN_TYPE, "ePPN"),
        (GROUP_TYPE, "Group ID"),
        (DNS_TYPE, "Hostname"),
        (NONE_TYPE, "Anyone"),
    )

    def __init__(self, name='', user_type=''):
        self.name = name
        self.user_type = user_type

    def is_uwnetid(self):
        return self.user_type == self.UWNETID_TYPE

    def is_eppn(self):
        return self.user_type == self.EPPN_TYPE

    def is_group(self):
        return self.user_type == self.GROUP_TYPE

    def is_none(self):
        return self.user_type == self.NONE_TYPE

    def __eq__(self, other):
        return self.name == other.name and self.user_type == other.user_type

    def __str__(self):
        return "{name: %s, user_type: %s}" % (
            self.name, self.user_type)


class GroupMember():
    UWNETID_TYPE = "uwnetid"
    EPPN_TYPE = "eppn"
    GROUP_TYPE = "group"
    DNS_TYPE = "dns"

    TYPE_CHOICES = (
        (UWNETID_TYPE, "UWNetID"),
        (EPPN_TYPE, "ePPN"),
        (GROUP_TYPE, "Group ID"),
        (DNS_TYPE, "Hostname"),
    )

    def __init__(self, name='', member_type=''):
        self.name = name
        self.member_type = member_type

    def is_uwnetid(self):
        return self.member_type == self.UWNETID_TYPE

    def is_eppn(self):
        return self.member_type == self.EPPN_TYPE

    def is_group(self):
        return self.member_type == self.GROUP_TYPE

    def __eq__(self, other):
        return self.name == other.name and self.member_type == other.member_type

    def __str__(self):
        return "{name: %s, user_type: %s}" % (
            self.name, self.member_type)
