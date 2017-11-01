import os
import win32com.client
import time

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
        device = usb.DeviceID
        decoded = device.decode().upper()
        VID = decoded.strip("USB\VID_")[:4]
        PID = decoded.split("&")[1].strip("PID_")[:4]
        SID = decoded.split(PID)[1].strip("\\")
        if SID in sids and SID not in nouids:
            return (VID,PID,SID)
    return (None,None,None)
# ------------------------------------
'''
wmi = win32com.client.GetObject ("winmgmts:") 
for usb in wmi.InstancesOf ("Win32_USBHub"): 
    print usb.DeviceID 
'''
'''
# https://www.activexperts.com/admin/scripts/wmiscripts/python/
from win32com.client import GetObject

searchKey = '0123456789ABCDEF'
objWMI = GetObject('winmgmts:').InstancesOf('Win32_USBHub')
for obj in objWMI:
#  if obj.DeviceID.find(searchKey) >= 0:
	if obj.Availability != None:
		print("Availability:" + str(obj.Availability))
#	if obj.Caption != None:
#		print("Caption:" + str(obj.Caption))
	if obj.ClassCode != None:
		print("ClassCode:" + str(obj.ClassCode))
	if obj.ConfigManagerErrorCode != None:
		print("ConfigManagerErrorCode:" + str(obj.ConfigManagerErrorCode))
	if obj.ConfigManagerUserConfig != None:
		print("ConfigManagerUserConfig:" + str(obj.ConfigManagerUserConfig))
	if obj.CreationClassName != None:
		print("CreationClassName:" + str(obj.CreationClassName))
	if obj.CurrentAlternateSettings != None:
		print("CurrentAlternateSettings:" + str(obj.CurrentAlternateSettings))
	if obj.CurrentConfigValue != None:
		print("CurrentConfigValue:" + str(obj.CurrentConfigValue))
#	if obj.Description != None:
#		print("Description:" + str(obj.Description))
	if obj.DeviceID != None:
		print("DeviceID:" + str(obj.DeviceID))
	if obj.ErrorCleared != None:
		print("ErrorCleared:" + str(obj.ErrorCleared))
	if obj.ErrorDescription != None:
		print("ErrorDescription:" + str(obj.ErrorDescription))
	if obj.GangSwitched != None:
		print("GangSwitched:" + str(obj.GangSwitched))
	if obj.InstallDate != None:
		print("InstallDate:" + str(obj.InstallDate))
	if obj.LastErrorCode != None:
		print("LastErrorCode:" + str(obj.LastErrorCode))
#	if obj.Name != None:
#		print("Name:" + str(obj.Name))
	if obj.NumberOfConfigs != None:
		print("NumberOfConfigs:" + str(obj.NumberOfConfigs))
	if obj.NumberOfPorts != None:
		print("NumberOfPorts:" + str(obj.NumberOfPorts))
	if obj.PNPDeviceID != None:
		print("PNPDeviceID:" + str(obj.PNPDeviceID))
	if obj.PowerManagementCapabilities != None:
		print("PowerManagementCapabilities:" + str(obj.PowerManagementCapabilities))
	if obj.PowerManagementSupported != None:
		print("PowerManagementSupported:" + str(obj.PowerManagementSupported))
	if obj.ProtocolCode != None:
		print("ProtocolCode:" + str(obj.ProtocolCode))
	if obj.Status != None:
		print("Status:" + str(obj.Status))
	if obj.StatusInfo != None:
		print("StatusInfo:" + str(obj.StatusInfo))
	if obj.SubclassCode != None:
		print("SubclassCode:" + str(obj.SubclassCode))
	if obj.SystemCreationClassName != None:
		print("SystemCreationClassName:" + str(obj.SystemCreationClassName))
	if obj.SystemName != None:
		print("SystemName:" + str(obj.SystemName))
	if obj.USBVersion != None:
		print("USBVersion:" + str(obj.USBVersion))
	print("")
	print("########")
	print("")
'''
# ------------------------------------

class ADB(object):
    def __init__(self):
        # https://stackoverflow.com/questions/14654718/how-to-use-adb-shell-when-multiple-devices-are-connected-fails-with-error-mor
        self.android_serial = None # %ANDROID_SERIAL%
  
    def specific_device(self, directs_command):
        self.android_serial = directs_command

    def call(self, command):
        command_result = ''

        if self.android_serial:
            command_text = 'adb -s %s %s' % (self.android_serial, command)
        else:
            command_text = 'adb %s' % command
        print command_text
        results = os.popen(command_text, "r")
        while 1:
            line = results.readline()
            if not line: break
            command_result += line
        return command_result

    def devices(self):

        result = self.call("devices -l")
        devices = result.partition('\n')[2].replace('\n', '').split('\tdevice')
        return [device for device in devices if len(device) > 2]
        '''
        command_result = ''
        results = os.popen('adb devices -l', "r")
        while 1:
            line = results.readline()
            if not line: break
            command_result += line
        print command_result
        return command_result
        '''
        
    def get_serialno(self):
        '''
        adb shell 
        cd /sys/class/android_usb/f_accessory/device/
        or
        cd /sys/class/android_usb/android0/
        echo -n xxx > iSerial
        '''
        result = self.call("get-serialno")
        return result
        
    def upload(self, fr, to):
        result = self.call("push " + fr + " " + to)
        return result
    
    def get(self, fr, to):
        result = self.call("pull " + fr + " " + to)
        return result

    def install(self, param):
        data = param.split()
        if data.length == 1:
            result = self.call("install " + param[0])
        elif data.length == 2:
            result = self.call("install " + param[0] + " " + param[1])
        return result

    def uninstall(self, package):
        result = self.call("shell pm uninstall " + package)
        return result

    def clearData(self, package):
        result = self.call("shell pm clear " + package)
        return result

    def shell(self, command):
        result = self.call("shell " + command)
        return result
        
    def kill(self, package):
        result = self.call("kill " + package)
        return result

    def start(self, app):
        pack = app.split()
        result = "Nothing to run"
        if pack.length == 1:
            result = self.call("shell am start " + pack[0])    
        elif pack.length == 2:
            result = self.call("shell am start " + pack[0] + "/." + pack[1])
        elif pack.length == 3:
            result = self.call("shell am start " + pack[0] + " " + pack[1] + "/." + pack[2])
        return result

    def screen(self, res):
        result = self.call("am display-size " + res)
        return result

    def dpi(self, dpi):
        result = self.call("am display-density " + dpi)
        return result

    def screenRecord(self, param):
        params = param.split()
        if params.length == 1:
            result = self.call("shell screenrecord " + params[0])
        elif params.length == 2:
            result = self.call("shell screenrecord --time-limit " + params[0] + " " + params[1])
        return result

    def screenShot(self, output):
        self.call("shell screencap -p /sdcard/temp_screen.png")
        self.get("/sdcard/temp_screen.png", output)
        self.call("shell rm /sdcard/temp_screen.png")
        
    def server(self, action):
        result = self.call(action + "-server")
        return result


if __name__ == '__main__':
    debug = ADB()
    
    print "## adb kill-server ##"
    print debug.server('kill')
    
    print "## adb devices -l ##"
    print debug.devices()
    
    debug.specific_device("product:TC802A")
    
    '''
    print "## enter sleep mode ##"
    debug.shell("input keyevent 26")
    debug.shell("input keyevent 82")
    debug.shell("input swipe 50 50 800 50")
    '''
    print debug.shell("getprop sys.usb.vid")
    #debug.screenShot("./ss.png")
    
    print "## adb get-serialno ##"
    print debug.get_serialno()
    
    print('## List USB Devices ##')
    hw_usb_list_devices()
    
    print('## Get USB ID ##')
    vid, pid, sid = hw_usb_get_id(sids=['0123456789ABCDEF'])
    print "VID: " + str(vid)
    print "PID: " + str(pid)
    print "SID: " + str(sid)
