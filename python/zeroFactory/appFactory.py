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
from exceptions import *

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
            self.serializer = json
        elif self.format == 'pickle':
            self.serializer = pickle
        elif self.format == 'msgpack':
            self.serializer = msgpack

        # ZeroMQ
        self.context = zmq.Context()  # zmq Context
        if socketType == 'rep':
            self.socket = self.context.socket(zmq.REP)
        elif socketType == 'pull':
            self.socket = self.context.socket(zmq.PULL)

        # check if routes and currentModule exists
        if not routes or not currentModule:
            errorString = '''
                            Routes AND Current Module are REQUIRED.
                            '''
            raise Exception(errorString)

        try:
            self.socket.bind(bind)  # bind address from config
        except zmq.core.error.ZMQError as e:
            if e.strerror == 'Invalid argument':
                errorString = '''Bind address format: transport://adress:port'''
            elif e.strerror == 'Address in use':
                errorString = '''Binding address in use. Free up address first'''
            raise Exception(errorString)
        except TypeError:
            errorString = 'Bind address is required'
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
        try:
            while True:
                rawMessage = self.socket.recv()
                
                messageUnpacked = self.serializer.loads(rawMessage)


                # ok, so you unpacked the message... now validate it
                try:
                    message = validateJSONRPCMessage(messageUnpacked)
                except RequiredKeysMissing as e:  # damn, you passed in bad request
                    errorData = {'message': messageUnpacked}
                    errorMessage = '%s' % e
                    messageID = self._getMessageID(messageUnpacked)
                    errorDict = self.error(-32600, errorMessage, errorData, messageID)

                    self.reply(errorDict)
                    
                    # TO DO: LOGGING!
                    continue

                except UnknownMessageType as e:
                    errorMessage = '%s' % e
                    errorDict = self.error(-32700, errorMessage)
                    self.reply(errorDict)
                    
                    # TO DO: LOGGING!
                    continue

                # congrats! the message validated without errors
                try:
                    method = getattr(currentModule, self.routes[message['method']])
                except KeyError as e:  # method not found in the route
                    errorData = {'message': messageUnpacked}
                    errorMessage = '%s' % e
                    messageID = self._getMessageID(messageUnpacked)
                    errorDict = self.error(-32601, errorMessage, data, messageID)

                    self.reply(errorDict)
                    
                    # TO DO: LOGGING!
                    continue  

                # great! you found the method. Now call it!
                try:
                    result = method(message['params'])
                except KeyError as e:  # this means params are not in message
                    errorData = {'message': messageUnpacked}
                    errorMessage = '%s' % e
                    messageID = self._getMessageID(messageUnpacked)
                    errorDict = self.error(-32602, errorMessage, data, messageID)

                    self.reply(errorDict)

                    # TO DO: LOGGING!
                    continue
                
                if result:  # result should be a dict
                    self.reply(result)

                else:
                    continue  # what should be done: log, and continue

        finally:
            self.close()

    def reply(self, d):
        '''
            This function takes d, which is a RESPONSE dictionary (either SUCCESS or ERROR),
            Transforms it nicely into msgpack or whatnots that has been defined in format
            And then sends it.
        '''
        # TO DO: verify that d is a dict first
        messagePacked = self.serializer.dumps(d)
        
        try:
            self.socket.send(messagePacked)
        except zmq.core.error.ZMQError as e:
            if e.strerror == 'Operation not supported':  # this is to verify that it is an operation not supported case
                pass

    def error(self, code, errorMessage, data=None, messageID=-1):
        '''
            This function wraps errors. No shit sherlock.
        '''
        errorDict = ERRORMESSAGE
        errorDict['error']['code'] = code  # Invalid Request
        errorDict['error']['message'] = errorMessage
        errorDict['error']['data'] = data
        errorDict['id'] = messageID

        return errorDict

    def _getMessageID(self, message):
        try:
            messageID = message['id']
        except:  # all exceptions! Pokemon! Gotta Catch 'em all
            messageID = -1

        return messageID

    def close(self):
        '''
            To undo any bindings if necessary
        '''
        self.socket.close()
        return 'Socket closed'

