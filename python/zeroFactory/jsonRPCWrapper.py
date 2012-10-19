import msgpack
import json

from exceptions import *

SUCCESSMESSAGE = {
    "jsonrpc": "2.0",
    "result": None,
    "id": None
}

ERRORMESSAGE = {
    "jsonrpc": "2.0",
    "error": {
        "code": None,
        "message": None,
        "data": None
            },
    "id": None
}


def validateJSONRPCMessage(message):
    '''
    type(message) == dict
    '''
    if type(message) != dict:
        # if it is improper JSON, ValueError will be raised
        try:
            message = msgpack.unpackb(message)
        except:
            try:
                message = json.loads(message)
            except:
                # raise error
                errorString = '''The type of message passed in needs 
                                to be dict, msgpack or json'''
                raise UnknownMessageType(errorString)

    # check if "jsonrpc" == 2.0
    try:
        if message['jsonrpc'] != '2.0':
            errorString = '''JSON RPC version supplied is %s.
                             Only "2.0" is accepted.''' % message['jsonrpc']
            raise UnsupportedJSONRPCVersion(errorString)
    except KeyError:
        errorString = '"jsonrpc" is required in the message'
        raise RequiredKeysMissing(errorString)

    # check if key "method" exists
    # check if key "params" exists
    # check if key "id" exists
    for definedKeys in ['method', 'params', 'id']:
        if definedKeys not in message.keys():
            errorString = '%s is required in the message' % definedKeys
            raise RequiredKeysMissing(errorString)

    return message