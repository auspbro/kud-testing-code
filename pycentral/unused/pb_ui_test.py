"""
@copyright (c) 2016-2017 Synapse Product Development LLC ("Synapse").
All Rights Reserved. This file is subject to the terms and conditions
defined in the license obtained by you from Synapse.
"""
import time
from binascii import unhexlify
from api import Central
from struct import pack
import sys

import signal
import sys

anovaPb_MsgType_LOOPBACK = 0
anovaPb_MsgType_CLI_TEXT = 1
anovaPb_MsgType_SAY_HELLO = 2
anovaPb_MsgType_SET_TEMP_SETPOINT = 3
anovaPb_MsgType_GET_TEMP_SETPOINT = 4
anovaPb_MsgType_GET_SENSORS = 5
anovaPb_MsgType_SET_TEMP_UNITS = 6
anovaPb_MsgType_GET_TEMP_UNITS = 7
anovaPb_MsgType_SET_COOKING_POWER_LEVEL = 8
anovaPb_MsgType_GET_COOKING_POWER_LEVEL = 9
anovaPb_MsgType_START_COOKING = 10
anovaPb_MsgType_STOP_COOKING = 11
anovaPb_MsgType_SET_SOUND_LEVEL = 12
anovaPb_MsgType_GET_SOUND_LEVEL = 13
anovaPb_MsgType_SET_DISPLAY_BRIGHTNESS = 14
anovaPb_MsgType_GET_DISPLAY_BRIGHTNESS = 15
anovaPb_MsgType_SET_COOKING_TIMER = 16
anovaPb_MsgType_STOP_COOKING_TIMER = 17
anovaPb_MsgType_GET_COOKING_TIMER = 18
anovaPb_MsgType_CANCEL_COOKING_TIMER = 19
anovaPb_MsgType_SET_CHANGE_POINT = 20
anovaPb_MsgType_GET_CHANGE_POINT = 21
anovaPb_MsgType_CHANGE_POINT = 22
anovaPb_MsgType_SET_BLE_PARAMS = 23
anovaPb_MsgType_GET_BLE_PARAMS = 24
anovaPb_MsgType_GET_DEVICE_INFO = 25
anovaPb_MsgType_GET_FIRMWARE_INFO = 26
anovaPb_MsgType_SYSTEM_ALERT_VECTOR = 27
anovaPb_MsgType_COOKING_TIMER = 28
anovaPb_MsgType_MESSAGE_SPOOF = 29


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

def set_temp_setpoint(msg_num,setpoint):
    central.cmd_setpoint(msg_num, setpoint)
    time.sleep(1)

def get_temp_setpoint(msg_num):
    central.cmd_get_setpoint(msg_num)

def get_curr_temp(msg_num):
    central.cmd_get_cur_temp(msg_num)

def get_fw_info(msg_num):
    central.cmd_get_fw_info(msg_num)

def set_temp_units(msg_num, degree):
    central.cmd_set_temp_units(msg_num, degree)

def get_temp_uints(msg_num):
    central.cmd_get_temp_units(msg_num)

def get_dev_info(msg_num):
    central.cmd_get_dev_info(msg_num)

def get_ble_params(msg_num):
    central.cmd_get_ble_params(msg_num)

ident = sys.argv[2]
mac = to_mac(ident)
if mac:
    central.connect(mac=mac)
else:
    central.connect(adv_data=ident)
while(1):
    get_curr_temp(anovaPb_MsgType_GET_SENSORS)
    time.sleep(0.2)
    # test = raw_input("Input Test Num")
    # if int(test) == 1:
    #     setpoint = raw_input("Enter a new temp setpoint: ")
    #     set_temp_setpoint(anovaPb_MsgType_SET_TEMP_SETPOINT, int(setpoint))
    # elif int(test) == 2:
    #     get_temp_setpoint(anovaPb_MsgType_GET_TEMP_SETPOINT)
    # elif int(test) == 3:
    #     get_curr_temp(anovaPb_MsgType_GET_SENSORS)
    # elif int(test) == 4:
    #     get_fw_info(anovaPb_MsgType_GET_FIRMWARE_INFO)
    # elif int(test) == 5:
    #     degree = raw_input("Enter 0 for celcius and 1 for Farenheight")
    #     while int(degree) != 1 and int(degree) != 0:
    #         degree = raw_input("Enter 0 for celcius and 1 for Farenheight")
    #     set_temp_units(anovaPb_MsgType_SET_TEMP_UNITS,int(degree))
    # elif int(test) == 6:
    #     get_temp_uints(anovaPb_MsgType_GET_TEMP_UNITS)
    # elif int(test) == 7:
    #     get_dev_info(anovaPb_MsgType_GET_DEVICE_INFO)
    # elif int(test) == 8:
    #     get_ble_params(anovaPb_MsgType_GET_BLE_PARAMS)
    # else:
    #     break;


central.disconnect()
