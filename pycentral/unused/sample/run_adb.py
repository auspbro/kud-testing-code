import os
import subprocess


class Adb(object):
    """ Provides some adb methods """

    @staticmethod
    def adb_devices():
        """
        Do adb devices
        :return The first connected device ID
        """
        cmd = "adb devices"
        c_line = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
        if c_line.find("List of devices attached") < 0:  # adb is not working
            return None
        return c_line.split("\t")[0].split("\r\n")[-1]  # This line may have different format

    @staticmethod
    def pull_sd_dcim(device, target_dir='E:/files'):
        """ Pull DCIM files from device """
        print "Pulling files"
        des_path = os.path.join(target_dir, device)
        if not os.path.exists(des_path):
            os.makedirs(des_path)
        print des_path
        cmd = "adb pull /sdcard/DCIM/ " + des_path
        result = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        print result
        print "Finish!"
        return des_path

    @staticmethod
    def some_adb_cmd():
        p = subprocess.Popen('adb shell cd sdcard&&ls&&cd ../sys&&ls',
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return_code = p.poll()
        while return_code is None:
            line = p.stdout.readline()
            return_code = p.poll()
            line = line.strip()
            if line:
                print line
        print "Done"
