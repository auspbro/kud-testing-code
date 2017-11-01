import sys
import time
from connection_utils import connect_to_central
from binascii import hexlify
from struct import pack, unpack
from reset_by_jlink import reset

OTA_FILE = 2

# FIXME JS -- need a way to kick off make_ota_test.bat


files = (('imgA', 'imgA.bin'), ('imgB', 'imgB.bin'))

def send_file(img_path):
    try:
        central = connect_to_central()
        img = ''
        with open(img_path, 'rb') as f:
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
        else:
            print "transfer failed!"
    except Exception, e:
        print e
        sys.exit()
        running = False

    central.disconnect()
    time.sleep(.2)

def check_version(ver):
    remote_ver = ''
    while remote_ver == '':
        try:
            central = connect_to_central()
            remote_ver = central.git_tag_get()
            central.disconnect()
            central.sleep(.2)
        except:
            pass
    return remote_ver == ver


while True:
    for tag, img_path in files:
        send_file(img_path)
        print check_version(tag)
