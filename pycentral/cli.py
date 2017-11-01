"""
@copyright (c) 2016-2017 Synapse Product Development LLC ("Synapse").
All Rights Reserved. This file is subject to the terms and conditions
defined in the license obtained by you from Synapse.
"""
import time
from binascii import unhexlify
from api import Central
import sys

import signal
import sys


if len(sys.argv) < 3:
    print "cli.py <COM> | <SN/MAC>"
    print "e.g. cli.py COM14 d780692291b0"

if len(sys.argv) == 1:
    print "available COM ports for BLE:"
    import serial.tools.list_ports
    for p in serial.tools.list_ports.comports():
        if 'Bluegiga' in str(p):
            print '\t%s' %str(p)
    sys.exit(0)

central = Central(sys.argv[1])

if len(sys.argv) == 2:
    central.list_peripherals('Nano')
    central.disconnect()
    time.sleep(.1)
    sys.exit(0)

def to_mac(mac):
    for ch in ' -:':
        mac = mac.replace(ch, '')
    result = 0
    if len(mac) == 12:
        try:
            result = unhexlify(mac)
        except:
            pass
    return result


ident = sys.argv[2]
mac = to_mac(ident)
if mac:
    central.connect(mac=mac)
else:
    central.connect(adv_data=ident)

running = True
while running:
    try:
        ln = raw_input()
        central.cmd_cli((ln + '\n').decode('utf-8'))
    except:
        central.disconnect()
        time.sleep(.1)
        running = False
