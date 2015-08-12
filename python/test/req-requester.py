import zmq
import msgpack
import json
import pickle

REQUEST = {
			'jsonrpc': '2.0',
			'method': None,
			'params': None,
			'id': None

}

def setUp(socketType='req'):
	context = zmq.Context()
	socket = context.socket(zmq.REQ)
	socket.connect('tcp://127.0.0.1:1234')
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

socket = setUp()
OK = 0 

d = {1:2}  # giberrish message to be sent
message = send(socket, d)
expectedResponse = {
					'jsonrpc': '2.0', 
					'id': -1, 
					'error': {
								'message': '"jsonrpc" is required in the message',
								'code': -32600,
								'data': {
											'message': {1: 2}
										}
							}
				}

if message == expectedResponse:
	OK += 1

# Legit Request
d = REQUEST
d['method'] = 'create'
d['id'] = 1

message = send(socket, d)
expectedResponse = {
					'jsonrpc': '2.0',
					'result': 'createdFunction!',
					'id': 1
					}

if message == expectedResponse:
	OK += 1
else:
	print '\n\n %s expected. Got %s instead \n\n' % (expectedResponse, message)

# Request with unknown method
d = REQUEST
d['method'] = 'NotFoundInRoutes'
d['id'] = 2

message = send(socket, d)
expectedResponse = {
					'jsonrpc': '2.0', 
					'id': 2, 
					'error': {
								'message': "'NotFoundInRoutes' is not a valid method",
								'code': -32601,
								'data': {
											'message': {
														'params': None, 
														'jsonrpc': '2.0',
														'method': 'NotFoundInRoutes',
														'id': 2
														}
										}
							}
					}
if message == expectedResponse:
	OK += 1
else:
	print '\n\n %s expected. Got %s instead \n\n' % (expectedResponse, message)


# Request without parameters
d = {'jsonrpc': '2.0'}
d['method'] = 'create'
d['id'] = 3

message = send(socket, d)
expectedResponse = {
					'jsonrpc': '2.0',
					'id': 3, 
					'error': {
								'message': 'params is required in the message',
								'code': -32600,
								'data': {
										'message': {
													'jsonrpc': '2.0',
													'method': 'create',
													'id': 3
													}
										}
							}
					}
if message == expectedResponse:
	OK += 1
else:
	print '\n\n %s expected. Got %s instead \n\n' % (expectedResponse, message)

print OK