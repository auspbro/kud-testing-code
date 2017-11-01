#!/usr/bin/python
# -*- coding: UTF-8 -*-

import subprocess
import sys
import getopt
import csv
import re
import os
import time
import shutil

# -----------------------------------
current_folder = os.path.dirname(os.path.realpath(__file__))
parent_folder = os.path.abspath(os.path.join(current_folder, os.pardir))
grandpapa_folder = os.path.abspath(os.path.join(parent_folder, os.pardir))

workstation_folder_name = 'log'
tester_results_folder = os.path.join(current_folder, "Results")
logger_results_folder = os.path.join(current_folder, "log_files")

result_folder_name = 'result'
storage_folder = parent_folder
ws_storage_folder = os.path.join(storage_folder, workstation_folder_name)

# for criteria, ex: criteria_BFT.csv, criteria_FFT.csv
criteria_file_name = '{}_{}.csv'.format('criteria', workstation_folder_name)
criteria_file_full_path = os.path.join(current_folder, criteria_file_name)

csv_file_name = 'result.csv'
collect_file_name = '{}_{}.csv'.format('collect', workstation_folder_name)

device_sn = ""
test_time = ""
result_folder = ""
output_folder = ""
# -----------------------------------
  
def create_result_folder(sn=None):
    global device_sn, test_time, result_folder, output_folder
    
    device_sn = str(sn)
    
    test_time = time.strftime("%Y%m%d%H%M%S")
    
    # remove result files first
    result_folder = os.path.join(ws_storage_folder, device_sn, result_folder_name)
    if os.path.exists(result_folder):
        shutil.rmtree(result_folder)

    output_folder = os.path.join(ws_storage_folder, device_sn, test_time)
    '''
    # ROBOCOPY can creating destination directory.
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    print "current : " + current_folder
    print "parent : " + parent_folder
    print "grandpapa : " + grandpapa_folder
    print "storage : " + storage_folder
    print "ws_storage : " + ws_storage_folder
    print "result : " + result_folder
    print "output : " + output_folder
    print "tester : " + tester_results_folder
    
    print "logger : " + logger_results_folder
    '''
    print_info("create_result_folder done: {} and {}".format(result_folder,output_folder))

    
def backup_result_folder(sn=None):
    global device_sn, test_time, result_folder, output_folder
    
#    result_folder = os.path.join(ws_storage_folder, device_sn, result_folder_name)
    
    if os.path.exists(tester_results_folder):
        if os.path.exists(logger_results_folder):
            # ROBOCOPY faster than XCOPY
#            run_command = "XCOPY {} {} /D/K/Y/C/I/".format(logger_results_folder,result_folder)
            run_command = "ROBOCOPY {} {}\\. /MOVE /XA:SH /UNICODE /MT:128 > NUL".format(logger_results_folder, result_folder)
            os.system(run_command)
#            shutil.rmtree(logger_results_folder)
        run_command = "ROBOCOPY {} {} /MOVE /XA:SH /UNICODE /MT:128 > NUL".format(tester_results_folder, result_folder)
        os.system(run_command)
        
#        output_folder = os.path.join(ws_storage_folder, device_sn, test_time)
        run_command = "ROBOCOPY {} {} /MIR /XA:SH /UNICODE /MT:128 > NUL".format(result_folder, output_folder)
        os.system(run_command)

    print_info("backup_result_folder done: {} and {}".format(result_folder,output_folder))
# -----------------------------------
import color_console as cons

debug_flag_environ = 0

# for color_console
default_colors = cons.get_text_attr()
default_bg = default_colors & 0x0070

def print_info(prt):
    cons.set_text_attr(cons.FOREGROUND_CYAN | default_bg |
                        cons.FOREGROUND_INTENSITY)
    print("{}".format(prt))
    cons.set_text_attr(default_colors)


def print_warn(prt):
    cons.set_text_attr(cons.FOREGROUND_YELLOW | default_bg |
                        cons.FOREGROUND_INTENSITY)
    print("{}".format(prt))
    cons.set_text_attr(default_colors)


def print_error(prt):
    cons.set_text_attr(cons.FOREGROUND_RED | default_bg |
                        cons.FOREGROUND_INTENSITY)
    print("{}".format(prt))
    cons.set_text_attr(default_colors)


def print_log(prt):
    cons.set_text_attr(cons.FOREGROUND_GREY | default_bg |
                        cons.FOREGROUND_INTENSITY)
    print("{}".format(prt))
    cons.set_text_attr(default_colors)


def print_debug(prt):
    if debug_flag_environ:
        cons.set_text_attr(cons.FOREGROUND_MAGENTA | default_bg |
                            cons.FOREGROUND_INTENSITY)
        print("{}".format(prt))
        cons.set_text_attr(default_colors)


def print_pass(prt):
    cons.set_text_attr(cons.FOREGROUND_GREEN | default_bg |
                        cons.FOREGROUND_INTENSITY)
    print("{}".format(prt))
    cons.set_text_attr(default_colors)


def print_fail(prt):
    cons.set_text_attr(cons.FOREGROUND_RED | default_bg |
                        cons.FOREGROUND_INTENSITY)
    print("{}".format(prt))
    cons.set_text_attr(default_colors)

# -----------------------------------
def subprocess_execute(command, time_out=60, entry_console=False):
    print('++++++++++++++++ Executing command: ' + command)
    
    import subprocess
    from threading import Timer
    
    if entry_console:
        console = 'cmd.exe /c start '
        command = console + command
                                  
    kill = lambda process: process.kill()
#    cmd = ['ping', 'www.google.com']   
    prog = subprocess.Popen(
        command, shell=(sys.platform != 'win32'),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    my_timer = Timer(time_out, kill, [prog])
   
    try:    
        my_timer.start()
        stdout, stderr = prog.communicate()
        print stdout, stderr
        return stdout
    finally:
        my_timer.cancel()

        
def process_execute(command, entry_console=False):
    print('++++++++++++++++ Running command: ' + command)
    
    if entry_console:
        console = 'cmd.exe /c start '
        command = console + command
                                  
    process = subprocess.Popen(command, shell=(sys.platform != 'win32'),
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            print output.strip()
    rc = process.poll()
    return rc

    
def system_execute(command, time_out=60, entry_console=False):
    print('++++++++++++++++ Calling command: ' + command)
    
    import subprocess
    from threading import Timer
    '''
    try: 
        import win32process 
    except ImportError: 
        flags = 0 
    else: 
        flags = win32process.CREATE_NO_WINDOW 

    if entry_console:
        console = 'cmd.exe /c start '
        command = console + command
    '''

    kill = lambda process: process.kill()
#    cmd = ['ping', 'www.google.com']   
    prog = subprocess.Popen(command, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.STDOUT, 
#        universal_newlines=True, 
#        creationflags=flags, 
        shell=(sys.platform != 'win32')) 

    my_timer = Timer(time_out, kill, [prog])
   
    try:    
        my_timer.start()
        while True:
            output = prog.stdout.readline()
            if output == '' and prog.poll() is not None:
                break
            if output:
                print output.strip()
        rc = prog.poll()
        return rc
    finally:
        my_timer.cancel()
# -----------------------------------
# -----------------------------------
def ReadCSVasDict(csv_file):
    '''
    (header,values) = ReadCSVasDict(result_full_path)
    header = header.strip().split('\t')
    values = values.strip().split('\t')
    '''
    try:
        with open(csv_file) as csvfile:
            header = ''
            values = ''
            reader = csv.DictReader(csvfile)
            for row in reader:
#                print row['Row'], row['Name'], row['Country']
#                print row['ITEM'], row['VALUE'] #, row['RESULT']
                header += "{}\t".format(row['ITEM'])
                values += "{}\t".format(row['VALUE'])
            return (header,values)
    except IOError as (errno, strerror):
            print("I/O error({0}): {1}".format(errno, strerror))     
    return


def WriteDictToCSV(csv_file,csv_columns,dict_data):
	try:
		with open(csv_file, 'wb') as csvfile:
		    writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
		    writer.writeheader()
		    for data in dict_data:
		    	writer.writerow(data)
	except IOError as (errno, strerror):
	        print("I/O error({0}): {1}".format(errno, strerror)) 	
	return


def ReadCSVasList(csv_file):
    try:
        with open(csv_file) as csvfile:
            reader = csv.reader(csvfile, dialect='excel', quoting=csv.QUOTE_NONNUMERIC)
            data_list = []
            data_list = list(reader)
            return data_list
    except IOError as (errno, strerror):
            print("I/O error({0}): {1}".format(errno, strerror)) 	
    return


def WriteListToCSV(csv_file,data_list,csv_columns=[]):
    try:
        with open(csv_file, 'wb') as csvfile:
            writer = csv.writer(csvfile, dialect='excel', quoting=csv.QUOTE_NONNUMERIC)
            if csv_columns != []:
                writer.writerow(csv_columns)
            for data in data_list:
               writer.writerow(data)
    except IOError as (errno, strerror):
            print("I/O error({0}): {1}".format(errno, strerror)) 	
    return


def GetLastRowByCSV(csv_file):
    with open(csv_file, 'r') as csvfile:
        lastrow = None
        for lastrow in csv.reader(csvfile): pass
        return lastrow


def GetItemByCriteria(csv_file,itemStr):
    with open(csv_file) as csvfile:
        record = None
        for record in csv.reader(csvfile):
            # criteria_columns = ['ITEM','VALUE','MIN','MAX']
#            print record[0]
            if record[0] == itemStr:
                return record
        return None


def GetItemColumnByCSV(csv_file,itemStr,columnStr='RESULT'):
    with open(csv_file) as csvfile:
        # read the file as a dictionary for each row ({header : value})
       
        d_reader = csv.DictReader(csvfile)
#        headers = d_reader.fieldnames
#        print headers
        for record in d_reader: # row
#            print record
            #print value in Column for each row
            if record['ITEM'] == itemStr:
#                print record
#                print record[columnStr]
                return record[columnStr]

        '''
        reader = csv.reader(csvfile, dialect='excel', quoting=csv.QUOTE_NONNUMERIC)
        header = reader.next()
#        print(header)
        columns = list(zip(*reader))
        print columns
        for fields in reader:
            print fields
#        '''


def judge_cvs_result(result_path,item,value='',result='',comment=''):
    COMMENT_RUN_ERROR = 'run error'
    COMMENT_NO_VALUE = 'no value'
    COMMENT_NO_CRITERIA = 'no criteria'
    COMMENT_NOT_MATCH = 'not match'

#    print("csv: {}, {}, {}, {}".format(item,value,result,comment))

    csv_file = os.path.join(result_path, csv_file_name)
    
    csv_data_list = []
    # check criteria files exists
    if not os.path.isfile(csv_file):
        csv_columns = ['ITEM','RESULT','VALUE','CRITERIA','COMMENT']
    else:
        csv_columns = []
        csv_data_list = ReadCSVasList(csv_file)
        '''
        # using results_collect.py
        rows = ReadCSVasList(result_full_path)
        print rows[row_number][column_number]
        columns = map(list,zip(*rows))
        header = columns[0][1:]
        print header
        '''

    criteria = ''
    cItem  = ''
    cValue = ''
    cMin   = ''
    cMax   = ''

    comment_report = ''
    if ( value=='[]' or value.find('None')!=-1 or value=='' or value.find('N/A')!=-1 ):
#            or value.lower().find('fail')!=-1 
        comment = COMMENT_NO_VALUE
        result = "FAIL"
    # ---------- Special case�G begin ----------
    elif item == 'WIFI' or item =='BT':
        if value.count(':') == 5: # address format = 80:D2:1D:81:2C:3B
            result = 'PASS'
        else:
            comment = '{} and format=XX:XX:XX:XX:XX:XX'.format(COMMENT_NOT_MATCH)
            result = "FAIL"

    if item == 'USB_STICK':
        if value == '5000M':
            result = 'PASS'
            comment = 'USB 3.0'
        elif value == '[]':
            result = "FAIL"
            comment = '{} and No Disk'.format(COMMENT_NOT_MATCH)
        elif value=='480M':
            result = "FAIL"
            comment = '{} and USB 2.0'.format(COMMENT_NOT_MATCH)
    # ---------- Special case�G end ----------
    elif result == '':
        criteria = GetItemByCriteria(criteria_file_full_path, item)
        if criteria:
            cItem,cValue,cMin,cMax = criteria
#            print("criteria: {}, {}, {}, {}".format(cItem,cValue,cMin,cMax))
            result = "FAIL"
            comment_report = COMMENT_NOT_MATCH
            if cValue.upper() == value.upper():
                result = "PASS"
                comment_report = ''
            elif criteria[2] != '' and criteria[3] != '':
                if value != '':
                    pattern = re.compile(ur'^[-+]?[0-9]+\.[0-9]+$')
                    isFloat = pattern.match(value)
                    if isFloat:
                        value = float(value)
                    else:
                        value = int(value)
                    if criteria[2] != '':
                        if isFloat:
                            cMin = float(criteria[2])
                        else:
                            cMin = int(criteria[2])
                    else:
                        cMin = 0
                    if criteria[3] != '':
                        if isFloat:
                            cMax = float(criteria[3])
                        else:
                            cMax = int(criteria[3])
                    else:
                        cMax = 0
                    if cMin <= value <= cMax:
                        result = "PASS"
                        comment_report = ''
                    else:
                        comment_report = '{} & The value must be between {} and {}'.format(COMMENT_NOT_MATCH,cMin,cMax)
            else:
                comment_report = '{} & The value must be {}'.format(COMMENT_NOT_MATCH,cValue)
        else:
            result = "FAIL"
            comment_report = COMMENT_NO_CRITERIA
    if result == "Success":
        result = "PASS"
    if result == "Failure":
        result = "FAIL"
    if comment != '':
        if comment_report != '':
            comment = '{} and {}'.format(comment,comment_report)
    else:
        if comment_report != '':
            comment = '{}'.format(comment_report)
            
    if result == "FAIL" and comment == '':
        comment = COMMENT_RUN_ERROR
        
    if result == "PASS":
        print_pass("{:<15}: {:<18}: {} : {}".format(item,value,result,comment))
    else:
        print_fail("{:<15}: {:<18}: {} : {}".format(item,value,result,comment))
        
    csv_data_list.append([item,result,value,str(cValue),comment])

    WriteListToCSV(csv_file,csv_data_list,csv_columns)
#    csv_data_list = ReadCSVasList(csv_file)
#    print csv_data_list
    
    return (result,comment)

# -----------------------------------
def find_files(directory, pattern='*'):
    import fnmatch
#   files = find_files(result_folder,'*result.csv')
    if not os.path.exists(directory):
        raise ValueError("Directory not found {}".format(directory))

    matches = []
    for root, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            full_path = os.path.join(root, filename)
            if fnmatch.filter([full_path], pattern):
                matches.append(os.path.join(root, filename))
    return matches
    
    
def touch(fname):
    if os.path.exists(fname):
        os.utime(fname, None)
    else:
        open(fname, 'a').close()
        
# -----------------------------------
def sortdict(dct):
    # sort by key
    '''
    result_dict = sortdict(result_dict)
    # or
    keylist = result_dict.keys() 
    keylist.sort() 
    for key in keylist:
        print "%s: %s" % (key, result_dict[key])
    # or
    dict = sorted(result_dict.iteritems(), key=lambda d:d[1], reverse = True)
    print dict
    '''
    kys = dct.keys()
    kys.sort()
    from collections import OrderedDict
    d = OrderedDict()
    for x in kys: 
        for k, v in dct.iteritems():
            if (k == x):
                d[k] = v
    return d    
# -----------------------------------
    
# -----------------------------------

if __name__ == "__main__":
    csv_columns = ['Row','Name','Country']
    dict_data = [
        {'Row': 1, 'Name': 'Alex', 'Country': 'India'},
        {'Row': 2, 'Name': 'Ben', 'Country': 'USA'},
        {'Row': 3, 'Name': 'Shri Ram', 'Country': 'India'},
        {'Row': 4, 'Name': 'Smith', 'Country': 'USA'},
        {'Row': 5, 'Name': 'Yuva Raj', 'Country': 'India'},
        ]
    
    currentPath = os.getcwd()
    csv_file = currentPath + "sample.csv"
    
    WriteDictToCSV(csv_file,csv_columns,dict_data)
    
    ReadCSVasDict(csv_file)
    print criteria_file_full_path
    print GetItemByCriteria(criteria_file_full_path, itemStr='Linux_Ver')