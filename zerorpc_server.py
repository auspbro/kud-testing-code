import zerorpc
import api

import logging
logging.basicConfig()

class cmd_Proxy(object):
    def send_cmd(self, cmd):
        resp = api.send_cmd(cmd)
        print "============================="
        print repr("send : " + cmd)
        print "||||||||||||||||||||||||||||||"
        print repr(resp)
        print "============================="
        return resp

    def ser_read(self, count=1):
        resp = api.ser_read(count)
        print "============================="
        print repr("recv : " + str(count))
        print "||||||||||||||||||||||||||||||"
        print repr(resp)
        print "============================="
        return resp


s = zerorpc.Server(cmd_Proxy())
s.bind("tcp://0.0.0.0:4242")
print 'server start'
try:
    s.run()
except:
    api.shutdown()

print 'end'