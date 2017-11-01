#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os, sys
import subprocess
import datetime, time, signal
import yaml
from threading import Timer
import re
import environ as env


def GetSerialNumber():
    settings = {}
    with open('settings.yml', 'r') as infile:
        settings = yaml.load(infile)
        infile.close()
        
    env.print_debug('>> GetSerialNumber: {} <<'.format(settings['SN']))
    
    return settings['SN']
    
def SetSerialNumber(sn=None):
    settings = {}
    with open('settings.yml', 'r') as infile:
        settings = yaml.load(infile)
        infile.close()

    env.print_debug('>> SetSerialNumber: {} <<'.format(sn))
    
    if sn != None and sn != settings['SN']:
        settings['SN'] = sn
        with open('settings.yml', 'w') as outfile:
            yaml.dump(settings, outfile, default_flow_style=False)
            outfile.close()
    return settings['SN']

def yml_get_sn(test_item='test_lists\\temp.yml'):        
    with open(test_item, 'r+') as yml_file:
        yml_file.seek(0)
        lines = yml_file.readlines()
#        print lines
        FileCount = len(lines)
#        print(FileCount) 
        for idx in range(FileCount):
            line = lines[idx].strip()
            if 'Run: WrPCBASN' in line.strip():
                idx += 1
                line = lines[idx]                   
                idPosition = lines[idx].find('Para: ')
                if idPosition != -1:
                    serialnum = ''
                    serialnum = line[idPosition+len('Para: '):]
                    yml_file.close()
                    return serialnum
                break
        

def main():
    do_CtrlConsole = 1
    
    do_Genconfig = 1
    do_Reboot = 0
    do_HDMI = 1
    do_EVT = 1
    do_RSSI = 0
    do_Temp = 0
    do_Result = 1
    do_RunStatus = 1

    
    SN = ''
    
    # for do_RSSI
    hdmiStatus = 'FAIL'
    
    # for do_Result
    ResultDirectory = ''
    
    # for do_RunStatus
    RunStatus = 'FAIL'

    # --------- setting Host environment: begin ---------
    if do_CtrlConsole:
        os.system('cls')
    # --------- setting Host environment: end ---------
    
    if len(sys.argv) > 1:
        SN = str( SetSerialNumber(sys.argv[1]) )
    elif do_Genconfig:
        proc_command = 'python gui_genconfig.py'
        result = env.subprocess_execute(proc_command, 120).split('\n')
#        print result
        for line in result:
            if line.find('SerialNumber') != -1:
                report = line.split('SerialNumber: "')[1].replace('\n', '')
                SN = report.split('"')[0].replace('\n', '').lstrip()
                break
    else:
        SN = str( GetSerialNumber() )
    '''
    if SN == '':
        env.print_error('>> Please input Serial Number... <<')
        quit()
    '''
    
    if do_EVT:
        env.create_result_folder( SN )

    if do_Reboot:
        test_item = 'test_lists\\reboot.yml'
        proc_command = 'python simple_tester.py {}'.format(test_item)
        env.process_execute(proc_command)
        
    if do_HDMI:
        # HDMI_STATUS="$(cat /sys/class/drm/card0-HDMI-A-1/status)"
        # connected or disconnected
        test_item = 'HDMI'
        proc_command = 'python gui_pass_fail.py {}'.format(test_item)
        result = env.subprocess_execute(proc_command, 60)
        '''
        if result.strip() == 'PASS':
            hdmiStatus = 'connected'
        else:
            hdmiStatus = 'disconnected'
        print 'HDMI_STAT={}'.format(hdmiStatus)
        '''

        # current_folder -->> Results
        if not os.path.exists(env.tester_results_folder):
            os.makedirs(env.tester_results_folder)

        result_filename = os.path.join(env.tester_results_folder, 'HDMI_Status.cmd')
        env.touch(result_filename)
        with open(result_filename, 'w') as f_output_file:
#            f_output_file.write('HDMI_STAT={}'.format(hdmiStatus))
            f_output_file.write('HDMI_STAT={}'.format(result.strip()))
            f_output_file.close()
        
    if do_RSSI:
        test_item = 'test_lists\\RSSI.yml'
        proc_command = 'python simple_tester.py {}'.format(test_item)
        env.process_execute(proc_command)

    if do_Temp:
        test_item = 'test_lists\\temp.yml'
        proc_command = 'python simple_tester.py {} False'.format(test_item)

        # --------- update serialnum in file: begin ---------
        # replace temp.yaml 
        read_sn = None
        read_sn = str( yml_get_sn(test_item) ).strip()
        if read_sn != 'None' and read_sn != SN:
            env.print_info( "yaml_file: [%s] not match [%s]" % (read_sn, SN) )
            fileString = open(test_item, 'r').read().replace(read_sn, SN)
            open(test_item, 'w').write(fileString)
        
        # replace criteria_XXX.csv
        read_sn = None
        read_sn = str( env.GetItemColumnByCSV(env.criteria_file_full_path, 'RePCBASN', 'VALUE') ).strip()
        if read_sn != 'None' and read_sn != SN:
            env.print_info( "csv_file: [%s] not match [%s]" % (read_sn, SN) )
            fileString = open(env.criteria_file_full_path, 'r').read().replace(read_sn, SN)
            open(env.criteria_file_full_path, 'w').write(fileString)
        # --------- update serialnum in file: end ---------
        env.system_execute(proc_command)
        
    if do_EVT:
        test_item = 'test_lists\\kud_evt_full.yml'
        proc_command = 'python simple_tester.py {} False'.format(test_item)
        
        # --------- update serialnum in file: begin ---------
        # replace kud_evt_full.yaml 
        read_sn = None
        read_sn = str( yml_get_sn(test_item) ).strip()
        if read_sn != 'None' and read_sn != SN:
            env.print_info( "yaml_file: [%s] not match [%s]" % (read_sn, SN) )
            fileString = open(test_item, 'r').read().replace(read_sn, SN)
            open(test_item, 'w').write(fileString)
        
        # replace criteria_XXX.csv
        read_sn = None
        read_sn = str( env.GetItemColumnByCSV(env.criteria_file_full_path, 'RePCBASN', 'VALUE') ).strip()
        if read_sn != 'None' and read_sn != SN:
            env.print_info( "csv_file: [%s] not match [%s]" % (read_sn, SN) )
            fileString = open(env.criteria_file_full_path, 'r').read().replace(read_sn, SN)
            open(env.criteria_file_full_path, 'w').write(fileString)
        # --------- update serialnum in file: end ---------
        
        loop_time = 3
        cnt = 1
        while cnt <= loop_time:
            loop_start_time = time.time()
            env.print_info('\n>>>>>>>>>>>>>>>> loop: %d begin <<<<<<<<<<<<<<<<\n' % cnt )
            result = env.system_execute(proc_command, 120)
            env.print_info('\n>>>>>>>>>>>>>>>> loop: %d end <<<<<<<<<<<<<<<<\n' % cnt )
            
#            total_loop_time = time.time() - loop_start_time
#            loop_hours = int(total_loop_time/3600)
#            loop_mins = int((total_loop_time/60)%60)
#            loop_secs = int(total_loop_time%60)
#            print(">>>> Elapsed Time for loop test : {} hours {} minutes {} seconds <<<<\n".format(loop_hours, loop_mins, loop_secs))
            env.print_info( 'loop elapsed time: %#.8f seconds\n' %(time.time()-loop_start_time) )
 
            if result == 0:
                # system_execute return pass
                break
            else:
                cnt += 1
                '''
                if cnt < loop_time:
                    user_continue = 'y'
                    user_continue = raw_input('\nPress enter y to continue, n for stop...')
                    if user_continue == 'n' or user_continue == 'N':
                        break
                '''
        env.print_info('>>>>>> loop count: %d <<<<<<\n' % cnt )
    
    if do_Result and (do_EVT or do_Temp):
        if not SN:
            SN = GetSerialNumber()
        '''
        if not ResultDirectory:
            ResultDirectory = os.path.join(env.ws_storage_folder, SN, env.result_folder_name)
        proc_command = 'python gui_result.py True {}'.format(ResultDirectory)
        '''
        proc_command = 'python gui_result.py False'
#        env.process_execute(proc_command)
        result = env.subprocess_execute(proc_command, 5)
        if do_RunStatus:
            if result.find('FAIL') != -1:
                RunStatus = "FAIL"
            else:
                RunStatus = "PASS"

    if do_EVT:
        env.backup_result_folder( SN )
    
    if do_RunStatus and do_Result:
        print('\n')
        if RunStatus == 'FAIL':
#            env.print_fail('\nFAIL')
            env.print_fail('    *****    *    *****  *')
            env.print_fail('    *       * *     *    *')
            env.print_fail('    ****   *****    *    *')
            env.print_fail('    *      *   *    *    *')
            env.print_fail('    *     *     * *****  *****')
        else:
#            env.print_pass('\nPASS')
            env.print_pass('    ****     *     ****   ****')
            env.print_pass('    *   *   * *   *      *')
            env.print_pass('    ****   *****   ****   ****')
            env.print_pass('    *      *   *       *      *')
            env.print_pass('    *     *     *  ****   ****')

    print('\nGUI Runner Done.')

if __name__ == '__main__':
    while True:
        # run
        main()
        
        user_continue = 'y'
        env.print_warn('\nPress enter y to continue, n for stop...')
        user_continue = raw_input() #('\nPress enter y to continue, n for stop...')
        if user_continue == 'n' or user_continue == 'N':
            break