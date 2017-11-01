from __future__ import print_function
import sys
import time
from connection_utils import connect_to_central
from binascii import hexlify
from struct import unpack
central = connect_to_central()

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


def parse_log(obj):
    rev = unpack('<H', obj[:2])
    obj = obj[2:]
    print ('rev: %d' %rev)
    while len(obj):
        tlv_len, tlv_id, tlv_cat, tlv_time_stamp = unpack('<HBBI', obj[:8])
        print ('len:%d id:%d cat:%d ts=%08x' %(tlv_len, tlv_id, tlv_cat, tlv_time_stamp))
        data = obj[8:tlv_len]
        print ('data:', hexlify(data))
        obj = obj[tlv_len:]

while running:
    try:
        ln = raw_input("enter file handle> ")
        file_handle = int(ln)
        start_time = time.time()
        obj = central.bulk_transfer.get(file_handle)
        duration = time.time() - start_time
        print("downloaded %d bytes, in %.1f seconds" %(len(obj), duration))
        parse_log(obj)
        central.bulk_transfer.erase(file_handle)
    except Exception, e:
        print(e)
        running = False

central.disconnect()
time.sleep(.1)
