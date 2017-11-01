import serial
import time
import yaml
import datetime
import sys
import re
from settings import settings
from binascii import unhexlify
from pycentral.api_uart_adaptor import Central
import environ as env
import device_adb

'''
Anova console :
    DefaultBootPrompt = 'Anova MFG Shell'
    ShellPrompt = ''
    ShellSymbol = '$'  # regular user
Kernel console : 
    ShellPrompt = 'sh-3.2'
    ShellSymbol = '#'  # superuser: root user prompt
    DefaultBootPrompt = DefaultShellPrompt
Android console :
    ShellPrompt = 'root@UY8:/'
    ShellSymbol = '#'
    DefaultBootPrompt = DefaultShellPrompt
'''

ShellPrompt = 'sh-3.2'
ShellSymbol = '#'
DefaultShellPrompt = "{}{}".format(ShellPrompt,ShellSymbol)
DefaultShellPromptNewLine = "\r\n{}{}".format(ShellPrompt,ShellSymbol)

DefaultBootPrompt = DefaultShellPrompt

class CliLog:
    log = []
    resp_text =  ''
    cur_entry = None

def log_append_resp(resp):
    CliLog.resp_text += resp

def log_entry_start(cmd):
    if CliLog.cur_entry!= None:
        CliLog.cur_entry.update({'Time' : str(datetime.datetime.now())})
        CliLog.cur_entry.update({'Response': CliLog.resp_text})
        CliLog.resp_text = ''
        CliLog.log.append(CliLog.cur_entry)
    CliLog.cur_entry = {'Command' : cmd}

def cmd_log_get():
    return CliLog.log

def cmd_log_reset():
    CliLog.log = []
    CliLog.resp_text =  ''
    CliLog.cur_entry = None

def is_ble_uart(port_id):
    for p in serial.tools.list_ports.comports():
        if ('Bluegiga' in str(p)) and (port_id in str(p)):
            return True
    return False

try:
    connect_port = settings['CONNECT']
    if connect_port == 'ADB':
        adb = settings['ADB']
        if adb.has_key('SID'):
            print "Connected..."
            if adb['MODE'] == 'USB':
                connect_port += ' USB'
                ser = device_adb.get_device(serial=adb['SID'])
            else:
                connect_port += ' TCP'
                host = ''
                if adb.has_key('HOST'):
                    host = adb['HOST']
                else:
                    ser = device_adb.get_device(serial=adb['SID'])
                    host = ser.tcp_connect()
                ser = device_adb.get_device(serial=host)
#            print ser.get_prop('sys.usb.vid')
#            if adb['MODE'] == 'TCP':
#                ser.tcp_disconnect()
    else:
        uart = settings['UART']
        if is_ble_uart(uart['COM']):
            ser = Central(uart['COM'])
            ser.connect(mac=unhexlify(uart['DUT_MAC']))
        else:
            print "Connected..."
            ser = serial.Serial(uart['COM'],
                                int(uart['BAUD']),
                                timeout=int(uart['TIMEOUT']))
except Exception, e:
    print "Failed to connect to %s port!" % connect_port
    print "Please verify the contents of settings.yml..."
    print "stack-trace:"
    print e
    sys.exit()

def shutdown():
    ser.close()

def ser_read(count=1):
    c = ser.read(count)
    CliLog.resp_text += c
#    print CliLog.resp_text
    return c

wait_until_read = True
def send_cmd(cmd, flag_space=False):
    if ser == None:
        raise Exception("Serial Port is not connected!")

    if hasattr(ser, 'flushInput'):
        ser.flushInput()
    ser.flush()

    env.print_debug("Transmit [{}]".format(cmd))
    
    ser.write(cmd + '\n')
    log_entry_start(cmd)
    result = ''
    # for cmd retry
    if settings['ADB']['SID']:
        retry = settings['ADB'].get('RETRIES')
    else:
        retry = settings['UART'].get('RETRIES')
        
    timeout = int( settings['CMD_TIMEOUT'] ) # for cmd timeout
        
    initial = time.time()
    duration = 0
    
    while wait_until_read and (retry is None or retry > 0):
        s = ser_read()
        if s == DefaultShellPrompt:
            break
        result += s
        
        '''
        # check in statements ">". and send "'" to exit
        if cmd==' EOFEOF ' and result.find('>') != -1:
            cmd = "'"
            ser.write(cmd + '\n')
        '''
        
        duration = time.time() - initial
        if duration > 1:
            sys.stdout.write( '\rElapsed Time: %#.8f seconds' % duration )
            sys.stdout.flush()
        
        if flag_space and len(s) < 1:
            if retry is not None:
                retry -= 1
            print "wait..."
        else:
            if retry is not None and duration > timeout:
                retry -= 1
                
                # check in statements ">". and send "'" to exit
                test_cmd = 'exit'
                ser.write(test_cmd + '\n')
                '''
                result = ser_read( len(DefaultShellPrompt) )
                if result.find('>') != -1:
                    test_cmd = "'"
                    ser.write(test_cmd + '\n')
                '''
                env.print_error('\nTimeout (%#.8f > %s) !!! please wait...' % (duration, timeout) )
                ser.write(cmd + '\n')
            if result.find(DefaultShellPromptNewLine) != -1:
                break

    ser_read()

    if duration > 1:
        sys.stdout.write('\n')
        sys.stdout.flush()

    env.print_debug("Receive [{}]".format(result))

    # Remove unwanted characters in resp
    result = result.replace(cmd, "")
    result = result.replace(DefaultShellPromptNewLine, "")
    result = result.strip()
        
    return result
    
def wait_for_boot():
    ln = ''
    found = False
    while True:
        ln += ser_read()
        if not found and (DefaultBootPrompt in ln):
            found = True
        if found and (DefaultShellPrompt in ln):
            print(">> boot success... <<")
            break
#    return ln
    
def cmd_int_get(cmd):
    """
    send a query with an integer response
    """
    return int(send_cmd(cmd).split('\n')[1])


def unpack_hash(result):
    """
    unpack hashed results
    """
    values = {}
    result = result.replace(' ', '').replace('\n', '').lower().split(',')
    for val in result:
        name, value = val.split(':')
        values.update({name: float(value)})
    return values


def cmd_hash_get(cmd):
    """
    send a query that has a hash table response
    """
    return unpack_hash(send_cmd(cmd))
    
# ============== test items ==============
    
def bsp_version():
#    results = send_cmd("getprop | grep ro.custom.build.version")
#    results = send_cmd('dmesg | grep "Linux version"')
    results = send_cmd('uname -n')
    env.print_warn( results )
    return results

def wifi_mac():
    # https://askubuntu.com/questions/628383/output-only-mac-address-on-ubuntu
    results = send_cmd("ifconfig mlan0 | perl -lane 'if(/^\w/&&$#F==4){print $F[$#F]}'")
#    sleep(1)
#    results = ser_read(1025)
    env.print_warn( results )
    return results

def wifi_ap_rssi(AccessPoint=[]):
    print('>> Scanning wifi access point... please wait. <<')

    # initialization
    send_cmd("ifconfig mlan0 up")
    time.sleep(0.5)
    send_cmd("ifconfig mlan0 up")
    time.sleep(0.5)
    
    # run commands
    results = send_cmd('iw dev mlan0 scan | egrep "signal|SSID|freq"').split('\n')
    index=0           
    while index < len(results):
        '''
        todo Delete: 
        * center freq segment 1: 0
        * center freq segment 2: 0
        '''
        if results[index].find("center freq segment") != -1:
            print("[%d] %s" %(index, results[index]))
            del results[index]
            continue
        index+=1
        
    scan_dict = {}
#    scan_list = []
    for idx in range(0, (len(results)/3)):
        '''
        todo Parse:
        [0] freq: 2xxx OR 5xxx
        [1] signal: -53.00 dBm
        [2] SSID: CM512-68503d
        '''
        ssid = results[(idx*3)+2].replace("SSID:", "").strip()
        if ssid != "\\x00":
            freq = results[(idx*3)].replace("freq:", "").strip()
            signal = results[(idx*3)+1].replace("signal:", "").replace("dBm", "").strip()
            env.print_warn("{:<30}: {:<5}: {} dBm".format(ssid, freq, signal))
            scan_dict[ssid] = signal
#            scan_list.append({ ssid : float(signal), }) 
#    env.print_warn( scan_dict )

    rssi_list = []
    for find_ap in AccessPoint:
        if find_ap in scan_dict:
#            print find_ap + " : " + scan_dict[find_ap]
            rssi_list.append(scan_dict[find_ap])
        else:
            rssi_list.append('-None.None')
#    print rssi_list
    
    if AccessPoint == []:
        return ' '.join(scan_dict)
    else:
        return ' '.join(rssi_list)
        
def bluetooth_device_rssi(Device=[], ScanTime='15'):
    print('>> Scanning bluetooth devices... please wait. <<')
    
    # initialization        
    CreateFile = '/tmp/bluetoothconfig.sh'
    send_cmd("rm %s" % CreateFile)
    
    # create run config
#    send_cmd('echo "#!/bin/bash" >> %s' % CreateFile)
    send_cmd('echo "echo -e \"power on\"" >> %s' % CreateFile)
    send_cmd('echo "sleep 2" >> %s' % CreateFile)
    send_cmd('echo "echo -e \"scan on\"" >> %s' % CreateFile)
    send_cmd('echo "sleep %s" >> %s' % (ScanTime,CreateFile))
    send_cmd('echo "echo -e \"quit\"" >> %s' % CreateFile)
    send_cmd('chmod a+x %s' % CreateFile)

    # run commands
    results = send_cmd('sh %s | bluetoothctl | grep RSSI | awk \'{print $4 \" \" $6}\'' % CreateFile).split('\n')
    
    # organize run commands results
    if results[0][:3] == 'sh ':
        del results[0]

    scan_dict = {}
    for line in results:
        items = line.strip().split(' ')
        env.print_warn("{} : {}".format(items[0], items[1]))
        scan_dict[items[0]] = items[1]
#    env.print_warn( scan_dict )
    
    rssi_list = []
    for find_dev in Device:
        if find_dev in scan_dict:
#            print find_dev + " : " + scan_dict[find_dev]
            rssi_list.append(scan_dict[find_dev])
        else:
            rssi_list.append('-None')
#    print rssi_list
    
    if Device == []:
        return ' '.join(scan_dict)
    else:
        return ' '.join(rssi_list)

def machine_wait_for_boot(DISPLAY_ENABLE=False, DISPLAY_TIME=1):
    env.print_warn("\n>> Waiting for Boot <<")
    results = ''
    found = False
    initial = time.time()
    while True:
        results += ser_read()

        duration = time.time() - initial
        if duration >= DISPLAY_TIME:
            if DISPLAY_ENABLE:
                print results
            else:
                sys.stdout.write( '\rElapsed Time: %#.8f seconds' % duration )
                sys.stdout.flush()
                
        if not found and (DefaultBootPrompt in results):
            if DISPLAY_ENABLE:
                print results
            found = True
        if found and (DefaultShellPrompt in results):
            env.print_warn("\n>> Boot Success ... <<")
            break
    return found
    
def machine_reboot(REBOOT_CMD='reboot',DISPLAY_ENABLE=False, DISPLAY_TIME=1):
    send_cmd( REBOOT_CMD ).split('\n')
    print machine_wait_for_boot(DISPLAY_ENABLE, DISPLAY_TIME)
    '''
    results = ''
    found = False
    while True:
        results += ser_read()
        if not found and (DefaultBootPrompt in results):
            found = True
        if found and (DefaultShellPrompt in results):
            env.print_warn(">> Reboot Success... <<")
            break
    return found
    '''
    '''
Starting syslogd/klogd: done
Starting OTA update engine ...
Starting jhid...
Starting OTA boot success notifier ...
    '''
    '''
    reboot_found = False
    results = results.split('\n')
    for line in results:
        if line.find("Starting OTA boot success notifier") != -1:
            env.print_warn( line )
            reboot_found = True
            break
    return reboot_found
    '''

def bios_update(BIOS_IMG='', FOLDER='', RETRY='3'):
    if BIOS_IMG != '':
        RETRY = int(RETRY)
        retry = RETRY
        while (retry > 0):
            env.print_warn(">> run bios_update : retry %d <<" % (RETRY-retry+1))
            sticks = send_cmd('ls /run/media/').split()
#            print sticks
            if len(sticks):
                for dev_name in sticks:
                    full_path = '/run/media/{}/{}/{}'.format(dev_name, FOLDER, BIOS_IMG)
                    exist_fv = send_cmd('ls {} | wc -l'.format(full_path))
                    if len(exist_fv.split('\n')) == 1 and int( exist_fv ) == 1:
                        env.print_pass("'{}' Found.".format (full_path))
                        send_cmd('mount -o remount, rw /esp')
                        send_cmd('cp {} /esp/BIOSUPDATE.fv'.format(full_path))
                        time.sleep(0.8)
                        exist_esp = send_cmd('ls /esp/BIOSUPDATE.fv | wc -l')
                        if len(exist_esp.split('\n')) == 1 and int( exist_esp ) == 1:
                            print len(exist_esp.split('\n'))
#                            return machine_reboot(DISPLAY_ENABLE=False)       
                            return True
                    else:
                        env.print_fail("'{}' Not Found.".format (full_path))
            retry -= 1
    return False

        
def bios_version(BIOS_VER="CHT N276 v."):
    '''
    send_cmd("reboot").split('\n')
    results = wait_for_boot().split('\n')

    results = send_cmd('dmesg | grep "%s"' % BIOS_VER).split('\n')
    bios_ver = ''
    for line in results:
        if line.find(BIOS_VER) != -1:
            bios_ver = line.replace(BIOS_VER, "").strip()
            env.print_warn( line )
            break
    '''
    results = send_cmd('dmesg | grep "%s"' % BIOS_VER)
    bios_ver = ''
    pattern = re.compile(ur'\d+(?:\.\d+){2}', re.MULTILINE)
    bios_ver = re.findall(pattern, results)[0]

    return bios_ver

def run_manufacturing_mode(CMD='', PARA='', SLEEP='0', RETRY='3'):
    # initialize
    CreateFile = "/tmp/{}.sh".format(CMD)
    LogFile = "/tmp/{}.log".format(CMD)
    send_cmd("rm /tmp/%s*" % CMD)
    
    RETRY = int(RETRY)
    retry = RETRY
    results = ''
    while (retry > 0):
        # create run config: parameter
        if PARA:
            send_cmd('echo "echo -e %s %s" > %s' % (CMD, PARA, CreateFile))
        else:
            send_cmd('echo "echo -e %s" > %s' % (CMD, CreateFile))
        time.sleep(0.1)
        
        if int(SLEEP) > 0:
            send_cmd('echo "sleep %d" >> %s' % (SLEEP, CreateFile))

        send_cmd('echo "echo -e exit" >> %s' % CreateFile)
        time.sleep(0.1)
        
        # run commands
        results = send_cmd("sh %s | MFMStart > %s ; cat %s" % (CreateFile, LogFile, LogFile))
        env.print_log("\nResults=[{}], lenght={}\n".format(results, len(results.split('\n'))))

        # check error
        if ( len(results.split('\n'))<2 or results.count(': ')<2 # or results.find("Manufacturing mode: On") == -1
#                or results.find("command not found")!=-1 or results.find("command failed")!=-1 or results.find("Unknown Command")!=-1
                or results.find("EOFError")!=-1 or results.lower().find("command")!=-1
                or results.find("Read-only")!=-1 or results.find("No such file or directory")!=-1):
            env.print_warn(">> run %s : retry %d <<" % ( CMD, (RETRY-retry+1)))
            env.print_error(results)
            retry -= 1
        else:
            return results
    if len(results.split('\n'))<=1 or results.find("No such file or directory")!=-1 or results.find("command not found")!=-1:
        results = "%s: ERROR" % CMD
    return results
    
if __name__ == "__main__":
#    wait_for_boot()
#    print "---- machine_reboot ----"
#    machine_reboot('reboot')
#    send_cmd( 'reboot' )
    machine_reboot()
    
    print "---- bios_version ----"
    print bios_version()
    '''
    print "---- bsp_version ----"
    print bsp_version()

    print "---- wifi_mac ----"
    print wifi_mac()

    print "---- wifi_ap_rssi ----"
    wap = ['TP-LINK_SE', 'Guest']
    print wifi_ap_rssi(wap)

    print "---- bt_device_rssi ----"
    bt_dev = ['A0:88:69:46:45:CD']
    print bluetooth_device_rssi(bt_dev)
    '''