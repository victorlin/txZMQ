Twisted bindings for 0MQ
========================

.. contents::

Introduction
------------

.. note::

    This is not the `original version of txZMQ`_, this is a refactoried version
    of txZMQ by Victor Lin.
    
    .. _`original version of txZMQ`: http://pypi.python.org/pypi/txZMQ

txZMQ allows to integrate easily `0MQ <http://zeromq.org>`_ sockets into
Twisted event loop (reactor).

txZMQ supports both CPython and PyPy.

Improvement
-----------

Original API design of txZMQ was wrongly designed, and they are not reusable or
hard to use,  for example, to set HWM of a ZeroMQ socket, you need to change 
the class level variable.::

    from txzmq import ZmqConnection
    ZmqConnection.highWaterMark = 100
    conn = ZmqConnection(factory)
    
As you can see the highWaterMark variable affects all connection made afterward.
This is obviously not a good design. 

Also, the encapsulation of endpoints is not necessary. Sometimes you may need
to connect or bind a address after a ZmqConnection was created, original 
design has no obvious way to do it. You need to pass endpoints when create a
new ZmqConnection.

PUSH/PULL and PAIR connections are not present in original version. I add
those connection types in this library.

There is also `a serious bug`_ in original version. When read signal
of FD is triggered before reactor perform another select, then txZMQ stop
reading from that socket anymore. This version fixes the bug. 

.. _`a serious bug`: https://github.com/smira/txZMQ/pull/3

Requirements
------------

Non-Python library required:

* 0MQ library >= 2.1 (heavily tested with 2.1.4)

Python packages required:

* pyzmq (for CPython)
* pyzmq-ctypes (for PyPy)
* Twisted


Details
-------

txZMQ introduces support for general 0MQ sockets by class ``ZmqConnection``
that can do basic event loop integration, sending-receiving messages in
non-blocking manner, scatter-gather for multipart messages.

txZMQ uses ØMQ APIs to get file descriptor that is used to signal pending
actions from ØMQ library IO thread running in separate thread. This is used in
a custom file descriptor reader, which is then added to the Twisted reactor.

From this class, one may implement the various patterns defined by 0MQ. For
example, special descendants of the ``ZmqConnection`` class,
``ZmqPubConnection`` and ``ZmqSubConnection``, add special nice features for
PUB/SUB sockets.

Request/reply pattern is achieved via XREQ/XREP sockets and classes ``ZmqXREQConnection``, 
``ZmqXREPConection``.

Push/pull pattern is achieved via classes ``ZmqPushConnection``, 
``ZmqPullConection``.

Finally, Pair pattern is achieved via classes ``ZmqPairConnection``.

Example
-------

Here is an example of using txZMQ::

    import os
    import sys
    import time
    from optparse import OptionParser
    
    from twisted.internet import reactor
    
    import zmq
    from txzmq import ZmqFactory, ZmqPubConnection, ZmqSubConnection
    
    parser = OptionParser("")
    parser.add_option("-m", "--method", dest="method", help="0MQ socket connection: bind|connect")
    parser.add_option("-e", "--endpoint", dest="endpoint", help="0MQ Endpoint")
    parser.add_option("-M", "--mode", dest="mode", help="Mode: publisher|subscriber")
    parser.set_defaults(method="connect", endpoint="epgm://eth1;239.0.5.3:10011")
    
    (options, args) = parser.parse_args()
    
    zf = ZmqFactory()
    
    def bind_or_connect(s):
        if options.method == 'bind':
            s.bind(options.endpoint)
        elif options.method == 'connect':
            s.connect(options.endpoint)
    
    if options.mode == "publisher":
        pub = ZmqPubConnection(zf)
        bind_or_connect(pub)
    
        def publish():
            data = str(time.time())
            print "publishing %r" % data
            pub.send(data)
    
            reactor.callLater(1, publish)
    
        publish()
    else:
        def doPrint(msgs):
            print "message received: %r" % (msgs, )
        sub = ZmqSubConnection(zf, callback=doPrint)
        sub.setsockopt(zmq.SUBSCRIBE, '')
        bind_or_connect(sub)
    
    reactor.run()


The same example is available in the source code. You can run it from the
checkout directory with the following commands (in two different terminals)::

    examples/pub_sub.py --method=bind --endpoint=ipc:///tmp/sock --mode=publisher

    examples/pub_sub.py --method=connect --endpoint=ipc:///tmp/sock --mode=subscriber

Hacking
-------

Source code for txZMQ is available at `github <https://github.com/victorlin/txZMQ>`_;
forks and pull requests are welcome.

To start hacking, fork at github and clone to your working directory. To use
the Makefile (for running unit tests, checking for PEP8 compliance and running
pyflakes), you will want to have ``virtualenv`` installed (it includes a
``pip`` installation).

Create a branch, add some unit tests, write your code, check it and test it!
Some useful make targets are:

* ``make env``
* ``make check``
* ``make test``

If you don't have an environment set up, a new one will be created for you in
``./env``. Additionally, txZMQ will be installed as well as required
development libs.
