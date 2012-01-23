#!env/bin/python

"""
Example txZMQ client.

    examples/pub_sub.py --method=bind --endpoint=ipc:///tmp/sock --mode=publisher

    examples/pub_sub.py --method=connect --endpoint=ipc:///tmp/sock --mode=subscriber
"""
import os
import sys
import time
from optparse import OptionParser

from twisted.internet import reactor

rootdir = os.path.realpath(os.path.join(os.path.dirname(sys.argv[0]), '..'))
sys.path.append(rootdir)
os.chdir(rootdir)

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
