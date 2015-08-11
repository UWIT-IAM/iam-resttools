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

    
# IRWS Profile (only recover part for now)
class Profile():
    validid = ''
    recover_email = None
    recover_email_date = None
    recover_sms = None
    recover_sms_date = None
    recover_block_code = None

    def json_data(self):
        prof = {}
        if self.recover_email != None: prof['recover_email'] = self.recover_email
        if self.recover_email_date != None: prof['recover_email_date'] = self.recover_email_date
        if self.recover_sms != None: prof['recover_sms'] = self.recover_sms
        if self.recover_sms_date != None: prof['recover_sms_date'] = self.recover_sms_date
        if self.recover_block_code != None: prof['recover_block_code'] = self.recover_block_code
        return {'profile':[prof]}

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
    category_code = ''
    category_name = ''
    contact_email = ''
    org_supervisor = ''

    wp_name = ''
    wp_department = ''
    wp_email = []
    wp_phone = ''
    wp_title = ''
    wp_address = ''
    wp_name = ''
    wp_publish = False

    college = ''
    department = ''
    home_department = ''
    mailstop = ''
    unit = ''

    emp_ecs_code = ''
    emp_status_code = ''

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
        if other==None: 
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
    category_code = ''
    category_name = ''

    college = ''
    department = ''

    source_code = ''
    source_name = ''
    # status: 1=active, 3=former
    status_code = ''
    status_name = ''
    pac = ''

    wp_publish = 'Y'

    in_feed = ''
    created = ''
    updated = ''

    def __eq__(self, other):
        if other==None: 
            return False
        return self.regid == other.regid


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
        if other==None: 
            return False
        return self.uwnetid == other.uwnetid



# IRWS Subscription
class Subscription():
    uwnetid = ''
    subscription_code = ''
    subscription_name = ''
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
    
