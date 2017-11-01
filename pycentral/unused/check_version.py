import sys
import time
from connection_utils import connect_to_central
from binascii import hexlify
from struct import pack, unpack
central = connect_to_central()

try:
    print central.git_tag_get()
    #central.bulk_transfer.reset()
except Exception, e:
    print e
    running = False

central.disconnect()
time.sleep(.1)
