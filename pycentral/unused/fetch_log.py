from __future__ import print_function
import sys
import time
from connection_utils import connect_to_central
from binascii import hexlify
from struct import unpack


central = connect_to_central()
if len(sys.argv) < 4:
    print("Error MUST specify destination file!")
    sys.exit()

file_handle = 1
start_time = time.time()
obj = central.bulk_transfer.get(file_handle)
duration = time.time() - start_time
print("downloaded %d bytes, in %.1f seconds" %(len(obj), duration))
central.bulk_transfer.erase(file_handle)
with open(sys.argv[3], 'wb') as f:
    f.write(obj)
    f.close()

central.disconnect()
time.sleep(.1)
