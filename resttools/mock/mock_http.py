"""
Contains objects used by the non-HTTP DAO implementations
"""
import json


class MockHTTP(object):
    """
    An alternate object to HTTPResponse, for non-HTTP DAO
    implementations to use.  Implements the API of HTTPResponse
    as needed.
    """
    status_code = 0
    content = ""
    headers = {}

    def read(self):
        """
        Returns the document body of the request.
        """
        return self.content

    def json(self):
        return json.loads(self.content)

    def getheader(self, field, default=''):
        """
        Returns the HTTP response header field, case insensitively
        """
        if self.headers:
            for header in self.headers:
                if field.lower() == header.lower():
                    return self.headers[header]

        return default
