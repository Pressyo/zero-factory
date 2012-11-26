import sys
import os
import zmq.green as zmq
import json
import pickle
import msgpack
import traceback

# fix import and weird WSGI path issues
abspath = os.path.abspath(os.path.dirname(sys.argv[0]))
parentdir = os.path.dirname(abspath)
sys.path.insert(1, parentdir)  # add current path
os.chdir(abspath)

from jsonRPCWrapper import *
from zeroFactoryExceptions import *


class App():

    __slots__ = ['routes', 'currentModule', 'socketType', 'bind', 'format']

    def __init__(self, routes=None, currentModule=None,
                socketType='rep', bind=None, format='msgpack', verbose=None):
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
        self.verbose = verbose
        self.bind = bind

        # format of the messages. Defaults to msgpack
        if self.format == 'json':
            self.serializer = json
        elif self.format == 'pickle':
            self.serializer = pickle
        elif self.format == 'msgpack':
            self.serializer = msgpack

        # check if routes and currentModule exists
        if not routes or not currentModule:
            errorString = '''
                            Routes AND Current Module are REQUIRED.
                            '''
            raise Exception(errorString)

        self._bind()

    def _bind(self):
        # ZeroMQ
        self.context = zmq.Context()  # zmq Context
        if self.socketType == 'rep':
            self.socket = self.context.socket(zmq.REP)
        elif self.socketType == 'pull':
            self.socket = self.context.socket(zmq.PULL)

        try:
            self.socket.bind(self.bind)  # bind address from config
        except Exception as e:
            if e.strerror == 'Invalid argument':
                errorString = '''Bind address format: transport://adress:port'''
            elif e.strerror == 'Address in use':
                errorString = '''Binding address in use. Free up address first'''
            else:
                errorString = '%s' % e
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
                if self.verbose:
                    print 'received %s' % messageUnpacked

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
                    # Temporary logging: PRINT!
                    print '%s' % errorDict
                    continue

                except UnknownMessageType as e:
                    errorMessage = '%s' % e
                    errorDict = self.error(-32700, errorMessage)
                    self.reply(errorDict)

                    # TO DO: LOGGING!
                    # Temporary logging: PRINT!
                    print '%s' % errorDict
                    continue

                # congrats! the message validated without errors
                try:
                    method = getattr(self.currentModule, self.routes[message['method']])
                except KeyError as e:  # method not found in the route
                    errorData = {'message': messageUnpacked}
                    errorMessage = '%s is not a valid method' % e
                    messageID = self._getMessageID(messageUnpacked)
                    errorDict = self.error(-32601, errorMessage, errorData, messageID)

                    self.reply(errorDict)

                    # TO DO: LOGGING!
                    # Temporary logging: PRINT!
                    print '%s' % errorDict
                    continue

                # great! you found the method. Now call it!
                result = None  # default for result
                try:
                    result = method(message['params'])
                except KeyError as e:  # this means params are not in message
                    errorData = {'message': messageUnpacked}
                    errorMessage = '%s' % e
                    messageID = self._getMessageID(messageUnpacked)
                    errorDict = self.error(-32602, errorMessage, errorData, messageID)

                    self.reply(errorDict)

                    # TO DO: LOGGING!
                    # Temporary logging: PRINT!
                    print '%s' % errorDict
                except TypeError as e:
                    errorData = {'message': messageUnpacked}
                    errorMessage = '%s' % e
                    messageID = self._getMessageID(messageUnpacked)
                    errorDict = self.error(-32602, errorMessage, errorData, messageID)
                    self.reply(errorDict)
                except:
                    print traceback.format_exc()
                    e = sys.exc_info()
                    errorType = e[0]
                    try:
                        errorMessage = e[1][0]
                    except IndexError:
                        errorMessage = e[1]

                    errorData = {'message': messageUnpacked}
                    errorMessage = '%s : %s' % (errorType, errorMessage)
                    messageID = self._getMessageID(messageUnpacked)
                    errorDict = self.error(-32603, errorMessage, errorData, messageID)
                    self.reply(errorDict)

                if result:  # result should be a dict or None
                    wrappedMessage = SUCCESSMESSAGE
                    wrappedMessage['result'] = result
                    wrappedMessage['id'] = messageUnpacked['id']
                    self.reply(wrappedMessage)

                    if self.verbose:
                        print 'sent %s' % wrappedMessage
                else:
                    methodCalled = messageUnpacked['method']
                    errorMessage = 'No results found :('
                    errorData = {'message': 'No Results found for method %s' % methodCalled}
                    messageID = self._getMessageID(messageUnpacked)
                    errorDict = self.error(-32404, errorMessage, errorData, messageID)
                    self.reply(errorDict)
        except Exception as e:
            # this shouldn't happen. You're fucked.
            if self.verbose:
                print(traceback.format_exc())
                print("RESTARTING THE APP GRACEFULLY")
            self.close()
            self._bind()
            self.run()

        finally:
            self.close()

    def reply(self, d):
        '''
            This function takes d, which is a RESPONSE dictionary (either SUCCESS or ERROR),
            Transforms it nicely into msgpack or whatnots that has been defined in format
            And then sends it. If it needs to be sent
        '''
        # TO DO: verify that d is a dict first
        messagePacked = self.serializer.dumps(d)

        try:
            self.socket.send(messagePacked)
        except zmq.core.error.ZMQError as e:
            if e.strerror == 'Operation not supported':  # This is what is returned if the socket is a PULL
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
