from base64 import b64encode, b64decode
from datetime import datetime


# IRWS Name
class Name():
    validid = ''
    formal_cname = ''
    formal_fname = ''
    formal_lname = ''
    formal_privacy = ''
    display_cname = ''
    display_fname = ''
    display_mname = ''
    display_lname = ''
    display_privacy = ''

    def json_data(self):
        return {"formal_cname": self.formal_cname,
                "formal_fname": self.formal_fname,
                "formal_lname": self.formal_lname,
                "formal_privacy": self.formal_privacy,
                "display_cname": self.display_cname,
                "display_fname": self.display_fname,
                "display_mname": self.display_mname,
                "display_lname": self.display_lname,
                "display_privacy": self.display_privacy,
                }

    def __eq__(self, other):
        return self.uwregid == other.uwregid


# IRWS Profile (only the recover data for now)
class Profile():
    validid = ''
    recover_block_reasons = []
    recover_contacts = []

    def json_data(self):
        return {
            'profile': [
                {"recover_contacts": self.recover_contacts,
                 "recover_block_reasons": self.recover_block_reasons
                 }
            ]}

    def __eq__(self, other):
        return self.uwregid == other.uwregid


# IRWS Person
class Person():
    regid = ''
    lname = ''
    fname = ''
    identifiers = {}

    # def __init__(self, *args, **kwargs):
    #     self.identifiers = {}


# IRWS UWhr Person
class UWhrPerson():
    validid = ''
    regid = ''
    studentid = ''
    birthdate = ''

    fname = ''
    lname = ''
    categories = []
    contact_email = []
    workday_home_email = ''
    org_supervisor = ''

    wp_name = ''
    wp_lname = ''
    wp_fname = ''
    wp_department = []
    wp_email = []
    wp_phone = []
    wp_title = []
    wp_address = []
    wp_publish = False

    college = ''
    department = ''
    home_department = ''
    mailstop = ''
    unit = ''

    emp_ecs_code = ''
    emp_status_code = ''
    workday_last_active = ''

    budget = ''
    faccode = ''
    source_code = ''
    source_name = ''
    status_code = ''
    status_name = ''

    pac = ''

    in_feed = ''

    created = ''
    updated = ''

    def __eq__(self, other):
        if other is None:
            return False
        return self.regid == other.regid


# IRWS Sdb Person
class SdbPerson():
    validid = ''
    regid = ''
    studentid = ''
    birthdate = ''

    fname = ''
    lname = ''
    categories = []

    college = ''
    department = ''

    source_code = ''
    source_name = ''
    # status: 1=active, 3=former
    status_code = ''
    status_name = ''
    pac = ''

    cnet_id = ''
    cnet_user = ''

    wp_publish = 'Y'

    in_feed = ''
    created = ''
    updated = ''

    def __eq__(self, other):
        if other is None:
            return False
        return self.regid == other.regid


# IRWS Supplemental Person
class SupplementalPerson():
    validid = ''
    regid = ''

    lname = ''
    categories = []
    contact_email = []
    comment_code = ''
    comment_name = ''
    sponsor_id = ''
    college = ''
    source_code = ''
    source_name = ''
    status_code = ''
    status_name = ''
    in_feed = ''
    id_proofing = {}

    created = ''
    updated = ''

    def __eq__(self, other):
        if other is None:
            return False
        return self.regid == other.regid


# IRWS Cascadia person
class CascadiaPerson():
    validid = ''
    regid = ''
    categories = []
    lname = ''
    fname = ''
    birthdate = ''
    department = ''
    in_feed = ''
    status_code = ''


# IRWS Scca person
class SccaPerson():
    validid = ''
    regid = ''
    categories = []
    lname = ''
    fname = ''
    birthdate = ''
    scca_company = ''
    scca_cca_eppn = ''
    scca_fhc_eppn = ''
    in_feed = ''
    status_code = ''


# IRWS GenericPerson
class GenericPerson():
    validid = ''
    regid = ''
    lname = ''
    fname = ''
    contact_email = []
    categories = []
    source_code = ''
    status_code = ''


# IRWS UWNetId
class UWNetId():
    uwnetid = ''
    accid = ''
    validid = ''
    uid = ''
    luid = ''
    disenfran = ''
    netid_code = ''
    netid_name = ''
    status_code = ''
    status_name = ''
    logname = ''
    created = ''
    updated = ''

    def json_data(self):
        return {"",
                }

    def __eq__(self, other):
        if other is None:
            return False
        return self.uwnetid == other.uwnetid


# IRWS Regid
class Regid():
    regid = ''
    entity_code = ''
    entity_name = ''
    status_code = ''
    status_name = ''

    created = ''
    updated = ''

    def __eq__(self, other):
        if other is None:
            return False
        return self.regid == other.regid


# IRWS Subscription
class Subscription():
    uwnetid = ''
    subscription_code = ''
    subscription_name = ''
    subscription_data = ''
    notify_code = ''
    status_code = ''
    status_name = ''
    logname = ''
    created = ''
    updated = ''

    def json_data(self):
        return {"",
                }

    def __eq__(self, other):
        return self.uwnetid == other.uwnetid


# IRWS PAC
class Pac():
    pac = ''
    expiration = ''

    def json_data(self):
        return {"",
                }


# IRWS QnA
class QnA():
    uwnetid = ''
    ordinal = ''
    question = ''
    answer = ''
