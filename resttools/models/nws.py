# NWS representations

class UWNetIdAdmin():
    name = ''
    role = ''
    def __init__(self, name='', role=''):
        self.name = name
        self.role = role


class UWNetIdPwInfo():
    min_len = 0
    last_change = ''
    def __init__(self, min_len=0, last_change=''):
        self.min_len = min_len
        self.last_change = last_change

