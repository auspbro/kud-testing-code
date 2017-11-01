# -*- coding: utf-8 -*-


import serial.tools.list_ports
from pycentral.api import Central
import time
import yaml

import sys
if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')

'''
import locale
if sys.stdout.isatty():
    default_encoding = sys.stdout.encoding
else:
    default_encoding = locale.getpreferredencoding()
'''

import device_adb
# get a list of the current devices

adb_list = device_adb.get_devices()

port_list = list(serial.tools.list_ports.comports())

settings = {}
with open('settings.yml', 'r') as f:
    settings = yaml.load(f)
    f.close()

if len(sys.argv) > 1:
    settings['CONNECT'] = sys.argv[1].upper()
    
if len(sys.argv) > 1 and sys.argv[1].lower() == 'ble':
    found = False
    for p in port_list:
        if 'Bluegiga' in str(p):
            found = True
            print('set ble port to : %s' % str(p))
            port = p[0]

    if not found:
        print('can\'t find bluegiga dongle')
        sys.exit(0)

    if len(sys.argv) > 2:
        settings['SN'] = str(sys.argv[2])

#    if len(sys.argv) > 2 and len(sys.argv[2]) > 11 and sys.argv[2][6:12] == '2291b0': #b09122
#    if len(sys.argv) > 2 and len(sys.argv[2]) > 11 and sys.argv[2][6:12] == '6564f8': #f86465
    if len(sys.argv) > 3 and len(sys.argv[3]) > 11:
        mac = sys.argv[3]
        settings['UART']['COM'] = port.decode('utf-8').encode('utf-8')
        settings['UART']['DUT_MAC'] = mac
#        settings['SN'] = mac
        
#        del settings['ADB']

        with open('settings.yml', 'w') as outfile:
            yaml.dump(settings, outfile, default_flow_style=False)
        print("==== config gen ====")
        print(yaml.dump(settings, default_flow_style=False))
        print("====================")
    else:
        print("mac addr format error")
        print("scaning...")
        central = Central(port)
        central.list_peripherals('Nano')
#        central.list_peripherals('MoveLife')
        central.disconnect()
        time.sleep(.1)
        sys.exit(0)

elif len(sys.argv) > 1 and sys.argv[1].lower() == 'uart':
    if len(sys.argv) > 2:
        settings['SN'] = sys.argv[2]
    if len(port_list) > 0 and 'Bluegiga' not in str(port_list[0]):
        print('set uart port to : %s' % str(port_list[0]))
        settings['UART']['COM'] = port_list[0][0].decode('utf-8').encode('utf-8')

#        del settings['ADB']
        
        with open('settings.yml', 'w') as outfile:
            yaml.dump(settings, outfile, default_flow_style=False)
        print("==== config gen ====")
        print(yaml.dump(settings, default_flow_style=False))
        print("====================")
    else:
        print('cat\'t find uart port!')
elif len(sys.argv) > 1 and sys.argv[1].lower() == 'adb':
    if len(sys.argv) > 2:
        settings['SN'] = str(sys.argv[2])
    if len(sys.argv) > 3:
        settings['ADB']['SID'] = sys.argv[3]
    else:
        if len(adb_list) > 0:
            print('set adb port to : %s' % str(adb_list[0]))
            settings['ADB']['SID'] = adb_list[0].decode('utf-8').encode('utf-8')
            
#            del settings['UART']
    
        else:
            print('cat\'t find adb port!')
    with open('settings.yml', 'w') as outfile:
        yaml.dump(settings, outfile, default_flow_style=False)
    print("==== config gen ====")
    print(yaml.dump(settings, default_flow_style=False))
    print("====================")

else:
    print("genconfig <uart> <sn>")
    print("genconfig <ble> <sn> <mac>")
    print("genconfig <adb> <sn> <sid>")
    
    print("\n")
    print("######## UART ########")
    for n, (port, desc, hwid) in enumerate(sorted(port_list), 1):
        sys.stderr.write('{} - {}\n'.format(port, desc))
    print("\n")
    print("######## ADB ########")
    if len(adb_list) > 0:
        print adb_list
    print("\n")
#from __future__ import print_function
#    map(lambda p: print(p), port_list)