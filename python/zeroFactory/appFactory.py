import sys
import os
import zmq
import json
import pickle
import msgpack

# fix import and weird WSGI path issues
abspath = os.path.abspath(os.path.dirname(sys.argv[0]))
parentdir = os.path.dirname(abspath)
sys.path.insert(1, parentdir)  # add current path
os.chdir(abspath)

from jsonRPCWrapper import *


class App():
    __slots__ = ['routes', 'currentModule', 'socketType', 'bind', 'format']
    def __init__(self, routes=None, currentModule=None,
                socketType='rep', bind=None, format='msgpack'):
        '''
            routes should be a dict. An example:
                routes = {
                        'create-recipe': 'createRecipe',
                        'retrieve-recipe': 'retrieveRecipe',
                        'update-recipe': 'updateRecipe',
                        'delete-recipe': 'deleteRecipe'
                        }

            currentModule MUST be passed in.
            currentModule is defined by the main module calling this class:
                currentModule = sys.modules[__name__]

        '''
        self.routes = routes  # routes to call
        self.currentModule = currentModule  # current module is declared
        self.socketType = socketType  # this is needed for run()
        self.format = format

        # format of the messages. Defaults to msgpack
        if self.format == 'json':
            self.messageDevice = json
        elif self.format == 'pickle':
            self.messageDevice = pickle
        elif self.format == 'msgpack':
            self.messageDevice = msgpack

        # ZeroMQ
        self.context = zmq.Context()  # zmq Context
        if socketType == 'rep':
            self.socket = self.context.socket(zmq.REP)
        elif socketType == 'pull':
            self.socket = self.context.socket(zmq.PULL)

        if bind:
            self.socket.bind(bind)  # bind address from config
        else:
            errorString = '''Bind address required.
                            It is in this format: transport://adress:port
                            '''
            raise Exception(errorString)

        if not routes or not currentModule:
            errorString = '''
                            Routes AND Current Module are REQUIRED.
                            '''
            raise Exception(errorString)

    def run(self):
        '''
            message received is in this format (we're using jsonrpc v2):
            see http://www.jsonrpc.org/specification
            message = {
                    "jsonrpc": "2.0",
                    "method": ___,
                    "params": {
                        'data1': ___,
                        'data2': ___,
                        },
                    "id": ___
        '''
        while True:
            rawMessage = self.socket.recv()
            
            try:
                messageUnpacked = self.messageDevice.loads(rawMessage)
            except (ValueError, IndexError):  # this is to say assuming the default pickle/json devices don't work
                messageUnpacked = msgpack.unpackb(rawMessage)

            # ok, so you unpacked the message... now validate it
            try:
                message = validateJSONRPCMessage(messageUnpacked)
            except RequiredKeysMissing:  # damn, you passed in bad json
                # TO DO: LOGGING!
                continue  # what should be done: log, and continue

            # congrats! the message validated without errors
            try:
                method = getattr(currentModule, self.routes[message['method']])
            except KeyError:  # method not found in the route
                # TO DO: LOGGING!
                continue  # what should be done: log, and continue

            # great! you found the method. Now call it!
            try:
                result = method(message['params'])
            except KeyError:  # this means params are not in message
                # TO DO: LOGGING!
                continue  # what should be done: log, and continue
            
            if result:
                if self.socketType == 'rep':
                    pass
                    # TO DO: reply the goddamn data
                else:
                    pass  # all is good if a result was replied
            else:
                # TO DO: LOGGING!
                continue  # what should be done: log, and continue

    def close():
        '''
            To undo any bindings if necessary
        '''
        self.socket.close()
        return 'Socket closed'

