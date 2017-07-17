# NWS representations
class UWNetIdAdmin():
    name = ''
    role = ''
    type = 'netid'

    def __init__(self, name='', role='', type='netid'):
        self.name = name
        self.role = role
        self.type = type


class UWNetIdPwInfo():
    min_len = 0
    last_change = ''
    kerb_status = 'Active'

    def __init__(self, min_len=None, last_change=None, kerb_status=None):
        self.min_len = min_len if min_len is not None else UWNetIdPwInfo.min_len
        self.last_change = last_change if last_change is not None else UWNetIdPwInfo.last_change
        self.kerb_status = kerb_status if kerb_status is not None else UWNetIdPwInfo.kerb_status
