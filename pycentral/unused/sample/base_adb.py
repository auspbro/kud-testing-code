
# http://www.jianshu.com/p/939e7d833599
import os
import subprocess

class AndroidDebugBridge(object):
    def call_adb(self, command):
        command_result = ''
        command_text = 'adb %s' % command
        results = os.popen(command_text, "r")
        while 1:
            line = results.readline()
            if not line: break
            command_result += line
        results.close()
        return command_result
    
    # check for any fastboot device
    def fastboot(self, device_id):
        pass
    
    # check device
    def attached_devices(self):
        result = self.call_adb("devices")
        devices = result.partition('\n')[2].replace('\n', '').split('\tdevice')
        flag = [device for device in devices if len(device) > 2]
        if flag:
            return True
        else:
            return False
            

    # check status
    def get_state(self): 
        result = self.call_adb("get-state") 
        result = result.strip(' \t\n\r') 
        return result or None

    # restart 
    def reboot(self, option): 
        command = "reboot" 
        if len(option) > 7 and option in ("bootloader", "recovery",): 
            command = "%s %s" % (command, option.strip()) 
        self.call_adb(command) 
        
    # push file from pc to device 
    def push(self, local, remote): 
        result = self.call_adb("push %s %s" % (local, remote)) 
        return result

    
    # pull file from device to pc
    def pull(self, remote, local): 
        result = self.call_adb("pull %s %s" % (remote, local)) 
        return result
        
    # sync 
    def sync(self, directory, **kwargs): 
        command = "sync %s" % directory 
        if 'list' in kwargs: 
            command += " -l" 
            result = self.call_adb(command) 
            return result 
            
    # open app
    def open_app(self,packagename,activity):
        result = self.call_adb("shell am start -n %s/%s" % (packagename, activity)) 
        check = result.partition('\n')[2].replace('\n', '').split('\t ') 
        if check[0].find("Error") >= 1: 
            return False 
        else: 
            return True

def main():
    device = AndroidDebugBridge()
    if device.attached_devices():
        print ok
    else:
        print("Please plug-in devices")
        
if __name__ == "__main__":
    main()