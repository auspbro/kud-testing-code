import sys
import time
from connection_utils import connect_to_central
from binascii import hexlify
from struct import pack, unpack
central = connect_to_central()
from reset_by_jlink import reset

OTA_FILE = 2

running = True
def is_byte_ramp(ramp):
    i = 0
    result = True
    while i < len(ramp):
        byte, = unpack('B', ramp[i])
        result = byte == (i & 0xFF)
        if not result:
            break
        i += 1
    return result

def make_file(size):
    result = ''
    for i in range(size):
        result += pack('B', i & 0xFF)
    return result

success = True
try:
    img = ''
    with open(sys.argv[3], 'rb') as f:
        img = f.read()
    print "preparing OTA bank..."
    central.bulk_transfer.erase(OTA_FILE)
    print "transfering image..."
    start_time = time.time()
    result = central.bulk_transfer.put(OTA_FILE, img)
    duration = time.time() - start_time
    if result:
        print "uploaded %d bytes, in %.1f seconds" %(len(img), duration)
        print "resetting device..."
        central.bulk_transfer.reset()
        success = True
    else:
        print "transfer failed!"
except Exception, e:
    print e
    running = False

central.disconnect()
time.sleep(.1)


if success:
    print "waiting for device to boot..."
    success = False
    while not success:
        try:
            central = connect_to_central()
            central.disconnect()
            time.sleep(.2)
            success = True
        except:
            pass

print "OK"
