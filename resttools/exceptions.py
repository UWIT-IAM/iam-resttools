"""
Contains the custom exceptions used by the restclients.
"""


class PhoneNumberRequired(Exception):
    """Exception for missing phone number."""
    pass

class InvalidPhoneNumber(Exception):
    """Exception for invalid phone numbers."""
    pass

class InvalidNetID(Exception):
    """Exception for invalid netid."""
    pass

class InvalidRegID(Exception):
    """Exception for invalid regid."""
    pass

class InvalidEmployeeID(Exception):
    """Exception for invalid employee id."""
    pass

class InvalidUUID(Exception):
    """Exception for invalid UUID."""
    pass

class InvalidSectionID(Exception):
    """Exception for invalid section id."""
    pass

class InvalidSectionURL(Exception):
    """Exception for invalid section url."""
    pass

class InvalidGroupID(Exception):
    """Exception for invalid group id."""
    pass

class InvalidIdCardPhotoSize(Exception):
    """Exception for invalid photo size."""
    pass

class InvalidEndpointProtocol(Exception):
    """Exception for invalid endpoint protocol."""
    pass

class InvalidCanvasIndependentStudyCourse(Exception):
    """Exception for invalid Canvas course."""
    pass

class InvalidCanvasSection(Exception):
    """Exception for invalid Canvas section."""
    pass

class InvalidGradebookID:
    """Exception for invalid gradebook id."""
    pass

class InvalidIRWSName(Exception):
    """Exception for invalid IRWS name."""
    pass

class DataFailureException(Exception):
    """
    This exception means there was an error fetching content
    in one of the rest clients.  You can get the url that failed
    with .url, the status of the error with .status, and any
    message with .msg
    """
    def __init__(self, url, status, msg):
        self.url = url
        self.status = status
        self.msg = msg

    def __str__(self):
        return ("Error fetching %s.  Status code: %s.  Message: %s." %
                (self.url, self.status, self.msg))
