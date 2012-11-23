============
Zero Factory
============

Zero Factory is an app factory for zeroMQ apps. To use::

    #!/usr/bin/env python
    import sys
    from zeroFactory import appFactory
    from methods import *
    
    currentModule = sys.modules[__name__]
    routes = {
                'create': 'createFunction',
                'retrieve': 'retrieve'
              }
    bind = 'tcp://*:1234'

    app = appFactory.App(routes=routes, currentModule=currentModule, bind=bind)
    
    app.run()  # this will essentially serve forever until stopped

============
Zero Wrapper
============

Zero wrapper is a standardized client for ZMQ apps. It has a nice feature that is not available on normal zmq patterns: request timeouts. 

It handles REQ/REP and PUSH/PULL clients well for now (well, you have to define it). To use::

    #!/usr/bin/env python
    import zmq
    from zeroFactory import appWrapper

    addresses = ['tcp://*:1234', 'ipc://address.socket']
    # addresses can be list or string

    context = zmq.Context()  # context has to be initialized before hand
    app = AppWrapper(context, zmq.REQ, addresses)

    message = "I'm sending this!"
    reply = app.sendRecv(message, 1)  # default time out is None. Meaning it will wait forever

The reason why the context has to be initialized before hand is because there will be times where you want many sockets to share the same context.