"""
@copyright (c) 2016-2017 Synapse Product Development LLC ("Synapse").
All Rights Reserved. This file is subject to the terms and conditions
defined in the license obtained by you from Synapse.
"""

import pkgutil # neaded to make py2exe happy
from central_base import *
from domain_manager import domain_manager
from cobs_transport import cobs_transport, cobs_transport_decoder
from struct import pack, unpack
from binascii import hexlify, unhexlify
from uuid import UUID
import sys
import time
import purdue_pb2 as pb
from bulk_transfer import BulkTransferAgent
from threading import Event
import win32com.client

def uuid(u):
    u = u.replace('-','')
    return UUID(u).bytes[::-1]


def anova_uuid(u):
    # python bled112_scanner.py -p COM7
    # MAC = B0912269818D
    # UUID = 0201061106684C05633E7742A28245F10A0000140E
    # 1504691228.419 -47 0 B0912269818D 0 255 0201061106684C05633E7742A28245F10A0000140E
    return uuid("0e14" + u + "-0af1-4582-a242-773e63054c68")

TX_UUID    = anova_uuid("0001")
RX_UUID    = anova_uuid("0002")
ASYNC_UUID = anova_uuid("0003")


MGMT_DOMAIN = 0
UPDT_DOMAIN = 1

(MSG_TYPE_LOOPBACK,
  MSG_TYPE_CLI_TEXT,
  MSG_TYPE_SAY_HELLO,
  MSG_TYPE_SET_TEMP_SETPOINT,
  MSG_TYPE_GET_TEMP_SETPOINT,
  MSG_TYPE_GET_CURR_TEMP,
  MSG_TYPE_SET_TEMP_UNITS,
  MSG_TYPE_GET_TEMP_UNITS,
  MSG_TYPE_SET_HEATING_RATE,
  MSG_TYPE_GET_HEATING_RATE,
  MSG_TYPE_START_HEATING,
  MSG_TYPE_STOP_HEATING,
  MSG_TYPE_SET_SOUND_LVL,
  MSG_TYPE_GET_SOUND_LVL,
  MSG_TYPE_SET_DISPLAY_BRIGHTNESS,
  MSG_TYPE_GET_DISPLAY_BRIGHTNESS,
  MSG_TYPE_SET_COOKING_CYCLE_TIMER,
  MSG_TYPE_GET_COOKING_CYCLE_TIMER,
  MSG_TYPE_CANCEL_COOKING_TIMER,
  MSG_TYPE_START_LOG,
  MSG_TYPE_DEL_LOG,
  MSG_TYPE_SET_BLE_PARAMS,
  MSG_TYPE_GET_BLE_PARAMS,
  MSG_TYPE_GET_DEV_INFO,
  MSG_TYPE_GET_FW_INFO,
  MSG_TYPE_SET_WIFI_CONFIG,
  MSG_TYPE_GET_WIFI_CONFIG,
  MSG_TYPE_GET_WIFI_FW_INFO) = range(28)

def find_tlv(data, target_type=0xFF):
    while len(data) >= 2:
        s, t = unpack('BB', data[:2])
        if t == target_type:
            data = data[2:s+1] # + 1 to acount for missing size byte
            break
        # skip the TLV
        data = data[s + 1:]
    return data

def get_mfg_info(data):
    dev_id, protocol, serial_num = (0, 0, 0)
    tlv = find_tlv(data, target_type=0xFF)
    if len(tlv) >= 2:
        mfg_id, = unpack('<H', tlv[:2])
        if mfg_id == 0xFFFF:
            # reserved ID
            if len(tlv) >= 14:
                dev_id, protocol = unpack('<HH', tlv[2:6])
                serial_num = tlv[6:]
            else:
                raise Exception ('Invalid MFG Info TLV')
    return dev_id, protocol, serial_num

class ApiCompletion(object):
    """
    used to store a procedure to be executed when the API function return
    """
    def __init__(self, handler):
        self._handler = handler

    def on_complete(self, data):
        """
        handle the on_complete event
        """
        (msg_type,) = unpack('B', data[0])
        if self._handler:
            self._handler(msg_type, data[1:])


def api_default_handler(msg_type, data):
    print "default_handler (msg_type=%d, data=%s)" %(msg_type, hexlify(data))

def pb_test_handler(msg_type, data):
    temp = pb.Temperature()
    temp.ParseFromString(data)
    print temp.decidegrees

def dummy_handler(msg_type, data):
    pass

def set_temp_setpoint_handler(msg_type, data):
    print "Sent new setpoint"

def get_temp_setpoint_handler(msg_type, data):
    temp = pb.IntegerValue()
    temp.ParseFromString(data)
    print "Setpoint: %d" %temp.value

def get_curr_temp_handler(msg_type, data):
    print "Sensors: "
    snsrList= pb.SensorValueList()
    snsrList.ParseFromString(data)
    print snsrList

def get_fw_info_handler(msg_type, data):
    info = pb.FirmwareInfo()
    info.ParseFromString(data)
    print "%s" %info.commitId
    print "%s" %info.tagId
    print "%s" %info.dateCode

def get_temp_units_handler(msg_type, data):
    temp = pb.IntegerValue()
    temp.ParseFromString(data)
    if temp.value == 0:
        print "Celcius"
    else:
        print "Farenheight"

def set_temp_units_handler(msg_type,data):
    print "Set new degree type"

def get_dev_info_handler(msg_type,data):
    dev = pb.DeviceInfo()
    dev.ParseFromString(data)
    print "Revision: %d" %dev.revision
    print "Model Num: %d" %dev.modelNumber
    print "Board Revision: %d" %dev.boardRevision
    print "BOM: %d" %dev.bom
    print "Platform:%d " %dev.platform
    print "CM Code:%d " %dev.cmCode
    print "Date Code: %d" %dev.dateCode
    print "%s" %dev.serialNumber

def get_ble_params_handler(msg_type, data):
    p = pb.BleConnectionParams()
    p.ParseFromString(data)

class BoundChar(object):
    def __init__(self, txchar, rxchar):
        self._txchar = txchar
        self._rxchar = rxchar
        rxchar.onAsyncReadResp = self._onResponse

    def writeNoResp(self, value):
        self._txchar.writeNoResp(value)

    # def onAsyncReadResp(self, value):
    #     pass

    def _onResponse(self, value):
        self.onAsyncReadResp(value)


class Central(object):
    def __init__(self, port):
        # Get the port used by the Bluegiga device from the command line arguments,
        # if it is specified.  Otherwise, use a hardcoded value
        self._central = bleCentral(port, 115200, 5, False)
        self._connObj = None
        self._transport = None
        self.bulk_transfer = BulkTransferAgent(self)

    def _char_get(self, uuid):
        """
        open characteristic
        """
        return self._connObj.getCharacteristicByUUID(uuid)

    def disconnect(self):
        """
        disconnect from the BLE
        """
        # Disconnect the BLE connection
        if self._connObj:
            self._connObj.close()
            self._connObj = None

    def list_peripherals(self, target='Nano'):
        """
        show all peripherals that match the target device name
        """
        self._central.scanAll(timeout=5)
        for resp in self._central.getResponses():
            if target in resp.data:
                device_id, protocol, serial_num = get_mfg_info(resp.data)
                print 'MAC=%s RSSI=%d Model=%d ProtoRev=%d, SN=%s' \
                    %(hexlify(resp.sender), resp.rssi, device_id, protocol, serial_num)

    def connect(self, adv_data=None, mac=None):
        """
        connect to the central
        """
        # Populate a list of discovered peripherals (no return value, use getResponses())
        self._central.scanAll(timeout=5)

        # Connect to our template_readwrite response object
        self._connObj = None
        if adv_data:
            self._connObj = self._central.connectByAdvertisementData(adv_data)
        if (not self._connObj) and mac:
            self._connObj = self._central.connectByAddress(mac)
        if not self._connObj:
            print "failed to connect.."
            self.disconnect()
            time.sleep(.1)
            sys.exit(0)
        tx_char = self._char_get(TX_UUID)
        rx_char = self._char_get(RX_UUID)
        bound_char = BoundChar(tx_char, rx_char)
        print "Connected..."

        self._transport = cobs_transport(bound_char,
                                        server_rx_buffer_size=1023,
                                        tx_block_size=20)
        rx_char.subscribeToReceiveNotificationsOnly()
        self._manager = domain_manager(self._transport)

        self._mgmt_domain = self._manager.add_domain(MGMT_DOMAIN)
        self._updt_domain = self._manager.add_domain(UPDT_DOMAIN)

        cli_char = self._char_get(ASYNC_UUID)
        self._cli_decoder = cobs_transport_decoder()
        cli_char.onAsyncReadResp = self._on_cli_text_received
        cli_char.subscribeToReceiveNotificationsOnly()

    def disconnect(self):
        """
        disconnect from the central
        """
        if self._transport != None:
            self._transport.shutdown()
        if self._central != None:
            self._central.shutdown()
        time.sleep(.1)

    def _on_cli_text_received(self, note):
        """
        handle receiving text from the CLI
        """
        for value in self._cli_decoder.process(note):
            self.on_cli_text_received(value)

    def on_cli_text_received(self, text):
        """
        invoked when CLI text is received
        """
        sys.stdout.write(text)


    def send(self, msg_type, data, handler=api_default_handler):
        """
        send data with specified message type
        """
        self._mgmt_domain.send(pack('<B', msg_type) + data,
                               ApiCompletion(handler))

    def bulk_transfer_send(self, msg_type, data, handler=api_default_handler):
        """
        send data with specified message type
        """
        self._updt_domain.send(pack('<B', msg_type) + data,
                               ApiCompletion(handler))

    def git_tag_get(self):
        evt = Event()
        self._resp = None
        def on_resp(msg_type, value):
            self._resp = value
            evt.set()

        self.send(MSG_TYPE_GET_FW_INFO, '', on_resp)
        evt.wait()
        return self._resp

    def cmd_loopback(self, data):
        self.send(msg_type=0, data=data)

    def cmd_cli(self, data, handler=dummy_handler):
        self.send(msg_type=1, data=data, handler = dummy_handler)

    def pb_test(self, data):
        self.send(msg_type=2, data=data, handler = pb_test_handler)

    def cmd_setpoint(self, msg_num, value):
    	iv = pb.IntegerValue()
        iv.value = value
        self.send(msg_type=msg_num, data=iv.SerializeToString(),  handler = set_temp_setpoint_handler)

    def cmd_get_setpoint(self, msg_num):
    	iv = pb.IntegerValue()
        iv.value = 0
        self.send(msg_type=msg_num, data = iv.SerializeToString(), handler = get_temp_setpoint_handler)

    def cmd_get_cur_temp(self, msg_num):
    	iv = pb.IntegerValue()
        iv.value = 0
        self.send(msg_type = msg_num, data = iv.SerializeToString(), handler = get_curr_temp_handler)

    def cmd_get_fw_info(self, msg_num):
    	iv = pb.IntegerValue()
        iv.value = 0
        self.send(msg_type = msg_num, data = iv.SerializeToString(), handler = get_fw_info_handler)

    def cmd_set_temp_units(self, msg_num, degree):
        iv = pb.IntegerValue()
        iv.value = degree
        self.send(msg_type = msg_num, data = iv.SerializeToString(), handler = set_temp_units_handler)

    def cmd_get_temp_units(self, msg_num):
        iv = pb.IntegerValue()
        iv.value = 0
        self.send(msg_type = msg_num, data = iv.SerializeToString(), handler = get_temp_units_handler)

    def cmd_get_dev_info(self, msg_num):
        iv = pb.IntegerValue()
        iv.value = 0
        self.send(msg_type = msg_num, data = iv.SerializeToString(), handler = get_dev_info_handler)

    def cmd_get_ble_params(self, msg_num):
        iv = pb.IntegerValue()
        iv.value = 0
        self.send(msg_type = msg_num, data = iv.SerializeToString(), handler = get_ble_params_handler)

def set_usb_status_by_devcon(status, devid, timeout=120):
    """
    using devcon to enable/disable the device.
    using it must download the devcon.exe, and put it under c:\
    """
    import subprocess, datetime, os, time, signal

    set_cmd = r"devcon.exe %s *VID_%s*" % (status, devid)

    start = datetime.datetime.now()
    process = subprocess.Popen(set_cmd)
    
    while process.poll() is None:
        time.sleep(0.1)
        now = datetime.datetime.now()
        if (now - start).seconds> timeout:
            os.kill(process.pid, signal.SIGKILL)
            os.waitpid(-1, os.WNOHANG)
            return None
    return process

def restart_windows_usb_by_devcon(devid, timeout=120):
    set_usb_status_by_devcon('disable', devid)
    set_usb_status_by_devcon('enable', devid)
        
def hw_usb():
    wmi = win32com.client.GetObject ("winmgmts:")
    devices = []
    for usb in wmi.InstancesOf ("Win32_USBHub"):
        device = usb.DeviceID
        decoded = device.decode().upper()
        VID = decoded.strip("USB\VID_")[:4]
        PID = decoded.split("&")[1].strip("PID_")[:4]
        SID = decoded.split(PID)[1].strip("\\")
        if VID.find("ROOT"):
            devices.append(VID + ":" + PID + ":" + SID)
    return devices
    
def hw_usb_list_devices():
    for device in hw_usb():
        print(device)
    print ('\n')

def hw_usb_get_id(sids=[],nouids=[]):
    wmi = win32com.client.GetObject ("winmgmts:")
    for usb in wmi.InstancesOf ("Win32_USBHub"):
#        print (usb.Name, usb.Description)
        device = usb.DeviceID
        decoded = device.decode().upper()
        VID = decoded.strip("USB\VID_")[:4]
        PID = decoded.split("&")[1].strip("PID_")[:4]
        SID = decoded.split(PID)[1].strip("\\")
        if SID in sids and SID not in nouids:
            return (VID,PID,SID)
    return (None,None,None)
        
if __name__ == "__main__":
    '''
    api = Api()
    api.connect()
    #    api.cmd_cli("hello\n".decode('utf-8'))
    #    api.cmd_cli("goodbye\n".decode('utf-8'))
    api.cmd_loopback("hello world!")
    '''
   
    print('## List USB Devices ##')
    hw_usb_list_devices()
    
    print('## Get USB ID ##')
    vid, pid, sid = hw_usb_get_id(sids=['0123456789ABCDEF'])
    print "VID: " + str(vid)
    print "PID: " + str(pid)
    print "SID: " + str(sid)
    
    restart_windows_usb_by_devcon(vid)