
import api
from Queue import Queue
import time
import yaml
import sys
import os
from test_logger import *
import math
import subprocess
import re


Logger = TestLog()

DEBUG = 0
def debug_print(prt):
    if DEBUG:
        print("{}".format(prt))


def is_int_in_range(val, limits):
    """
    verify that the int val passes the specified test-limits
    """
    min_val = float(limits['Min'])
    max_val = float(limits['Max'])
    if val:
        val = float(val)
    else:
        val = 0
    print min_val, max_val, val
    return (val >= min_val) and (val <= max_val)

def is_int_val(s):
    int_val = False
    try:
        int_val = math.floor(float(s)) == float(s)
    except:
        pass
    return int_val

#
# Available Test Procedures
#
def RecordDutID(test, args):
    print "-------- RecordDutID: begin --------"
    Logger.record(test.values[0])
    val = ''
    if is_int_val(test.values[0]):
        val = str(int(float(test.values[0])))
    print "-------- RecordDutID: end --------"
    return is_int_in_range(val, args) and (val != '')

def TestDutCompleted(test, args):
    print "-------- TestDutCompleted: begin --------"
    print 'test-dut-completed'
    Logger.save(api.cmd_log_get())
    api.cmd_log_reset()
    print "-------- TestDutCompleted: end --------"

def Dummy(test,args):
    return True

# ======== Commander begin ========

def extractresults(regex, resp):
    matches = re.finditer(regex, resp, re.MULTILINE)
    results = []
    for matchNum, match in enumerate(matches):
        matchNum = matchNum + 1
        values = []
        for groupNum in range(0, len(match.groups())):
            groupNum = groupNum + 1
            values.append(match.group(groupNum))
            # Sakia add : to debug Regex and Results.
            debug_print( "    item:" + str(matchNum-1) + ", index:" + str(groupNum-1) + ", value:" + str(match.group(groupNum)) )
        results.append(values)
    return results

def outputresult(test, result_list):
    try:
        path = r'.\Results'
        if not os.path.exists(path):
            os.makedirs(path)
    except Exception as e:
        print e
        pass
    with open(os.path.join(path,"%s.cmd" % test.test_id), 'w') as out_file:
        for k in result_list.keys():
            out_file.write("SET %s=%s\n" % (k, result_list[k]))

def Commander(test,args):
    if args.has_key("Cmds"):
        result_list = {}
        for c in args['Cmds']:
            if c.has_key("Cmd"):
                debug_print( '>>> RunCommand: %s  <<<' %c['Cmd'] )
                resp = api.send_cmd(c['Cmd'])
            elif c.has_key("Fun"):
                debug_print( '>>> RunFunction: %s  <<<' %c['Fun'] )
                if c['Args']:
                    resp = globals()[c['Fun']](test,c['Args'])
                else:
                    resp = globals()[c['Fun']](test,None)

            if c.get('Duration'):
                duration_sec = int(c['Duration'])
                time.sleep(duration_sec)
                resp = api.ser_read(1024) # will timeout after a second
                
            debug_print( '>>> RunResult: %s <<<' %resp )
            
            if c.get('Replace'):
                resp = resp.replace(c['Replace'][0], c['Replace'][1])
                debug_print( '>>> RunReplace: %s <<<' %resp )
            
            if c.get('Results'):
                if c.get('Regex'):
                    results = extractresults(c['Regex'], resp)
                else:
                    results = resp
                debug_print( '>>> RunRegex: %s <<<' %results )
                
                for r in c['Results']:
                    if r['type'] == 'int':
                        try:
                            result_list[r['name']] = int(results[r['item']][r['index']])
                        except:
                            result_list[r['name']] = ''
                    elif r['type'] == 'float':
                        try:
                            result_list[r['name']] = float(results[r['item']][r['index']])
                        except:
                            result_list[r['name']] = ''
                    elif r['type'] == 'string':
                        try:
                            result_list[r['name']] = results[r['item']:r['index']]
                        except:
                            result_list[r['name']] = ''
                    else:
                        try:
                            result_list[r['name']] = results[r['item']][r['index']]
                        except:
                            result_list[r['name']] = results

                    debug_print( '>>> RunResults: %s <<<' %results )
                    if result_list[r['name']] != '' and c.get('Unit'):
                        result_list[r['name']] = str(result_list[r['name']]) + c.get('Unit')
                        
                #workaround
#                if result_list.get('BLE_MAC_ADDR') is not None:
#                    result_list['BLE_MAC_ADDR'] = "".join(reversed([result_list['BLE_MAC_ADDR'][i:i+2] for i in xrange(0,len(result_list['BLE_MAC_ADDR']),2)]))

            if c.get('SleepTime'):
                time.sleep(c.get('SleepTime'))
               
#        print result_list
#        for k, v in result_list.items():
#            print(k, v)
        
        if len(result_list) > 0:
            outputresult(test, result_list)
            return result_list
    else:
        return False
        
    return True
# ======== Commander end ========

# ======== Function begin ========
def DeviceReboot(test, args):
    return api.machine_reboot(REBOOT_CMD=args['Cmd'],DISPLAY_ENABLE=args['Display'],DISPLAY_TIME=args['Time'])

def BiosUpdate(test, args):
    return api.bios_update(BIOS_IMG=args['Image'],FOLDER=args['Folder'],RETRY=args['Retry'])
    
def WirelessRSSI(test, args):
    WAP = [] # WAP : Wireless Access Point
    for line in args:
        WAP.append(args[line])
    return api.wifi_ap_rssi(WAP)
    
def BluetoothRSSI(test, args):
    scantimer = args['SCAN_TIME']
    BD = [] # BD : Bluetooth Device
    for line in args:
        if not line == 'SCAN_TIME':
            BD.append(args[line])
    return api.bluetooth_device_rssi(BD, ScanTime=scantimer)
    
def RunMFMStart(test, args):
    cmd = ''
    para = ''
    sleep = '0'
    result = True
    if args.has_key("Run"):
        cmd = args['Run']
        Logger.record({'Run': cmd})
        if args.has_key("Para"):
            para = args['Para']
            Logger.record({'Para': para})
        '''
        if args.has_key("Sleep"):
            sleep = args['Sleep']
            Logger.record({'Sleep': sleep})
        '''
    else:
        result = "RunMFMStart: ERROR"
    result = api.run_manufacturing_mode( cmd, PARA=para, SLEEP=sleep )
    Logger.record(result)
    return result
# ======== Function end ========