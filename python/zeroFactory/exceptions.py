'''
These exceptions are here to give meaningful messages when raised
'''


class UnsupportedJSONRPCVersion(BaseException):
    pass


class RequiredKeysMissing(BaseException):
    pass


class UnknownMessageType(BaseException):
	pass