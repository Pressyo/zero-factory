import zmq

'''
This is a standardized client for zeroFactory apps.
You may or may not want to include this in your apps.
The nice thing about this client wrapper is that it handles disconnects well.

It will basically close and reopen the socket if something bad happens.
'''


class AppWrapper:
    def __init__(self, context, socketType, addresses):
        '''
        Initialize the app you want to connect to by passing in all the details
        '''
        self.context = context
        self.socketType = socketType
        self.addresses = addresses
        self.socket = self.context.socket(socketType)
        self.connect()

    def connect(self):
        '''
        connect to app (zeroFactory or not)
        '''
        if type(self.addresses) == list or type(self.addresses) == tuple:
            for address in self.addresses:
                self.socket.connect(address)
        else:
            self.socket.connect(self.addresses)

    def reopen(self):
        self.socket.close()
        # reinitialize the socket
        self.socket = self.context.socket(self.socketType)
        self.connect()

    def send(self, message):
        '''
        zmq.NOBLOCK is for cases where the receipient does not exist
        '''
        self.socket.send(message, zmq.NOBLOCK)

    def recv(self):
        return self.socket.recv(zmq.NOBLOCK)

    def sendRecv(self, message, timeout):
        '''
        Usage:
        msg = app.sendRecv(messageSent, 1)

        This will automatically block until you have received a reply,
        or until timeout (in seconds)

        For high performance system and patterns (shotgun patterns for example)
        use a low timeout.
        '''
        self.send(message)
        poller = zmq.Poller()
        poller.register(self.socket, zmq.POLLIN)

        try:
            timeout = timeout * 1000
        except TypeError:
            timeout = None
        while True:
            socks = dict(poller.poll(timeout))
            if socks:
                if socks.get(self.socket) == zmq.POLLIN:
                    return self.recv()
            else:
                self.reopen()
                return None
