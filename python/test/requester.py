import zmq
import msgpack
import json
import pickle

def setUp():
	context = zmq.Context()
	socket = context.socket()
	socket.connect('tcp://*:1234')
	return socket

def send(socket, d, serializer=msgpack):
	try:
		messagePacked = serializer.dumps(d)
	except:
		messagePacked = serializer.packb(d)

	socket.send(messagePacked)
	msg = socket.recv()

	message = serializer.loads(msg)
	return message

def assert_ID_exists(message):
	try:  # tests begin!
		messageID = message['id']
	except TypeError:
		raise TypeError('wrong type received.')
	except KeyError:
		raise KeyError('no messageID')

def assert_Error(message, expectedError):
	'''
		pass in the code for expectedError
	'''
	try:
		error = message['error']
	except TypeError:
		raise TypeError('wrong type of message received')
	except KeyError:
		raise KeyError('not an error message')

	try:
		assert error['code'] == expectedError
		OK = 1
	except AssertionError:
		OK = 0
		pass

	return OK