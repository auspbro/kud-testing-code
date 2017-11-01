#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import sys
import glob
import csv

'''
from numpy import genfromtxt, savetxt
data = genfromtxt('in.txt')
savetxt('out.txt',data.T)
'''

current_folder = os.path.dirname(os.path.realpath(__file__))
parent_folder = os.path.abspath(os.path.join(current_folder, os.pardir))
grandpapa_folder = os.path.abspath(os.path.join(parent_folder, os.pardir))

workstation_folder_name = 'EVT3'
result_folder_name = 'result'
storage_folder = parent_folder
ws_storage_folder = os.path.join(storage_folder, workstation_folder_name)
csv_file_name = 'result.csv'
collect_file_name = '{}_{}.csv'.format('collect', workstation_folder_name)


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
    
if __name__ == '__main__':
    collect_full_path = os.path.join(ws_storage_folder, collect_file_name)
    
    if os.path.exists(collect_full_path):
        os.remove(collect_full_path)
    else:
        open(collect_full_path, 'a').close()

    header = []
    results = []

    os.chdir(ws_storage_folder)
    for sub_folder_name in os.listdir(ws_storage_folder):
#        print sub_folder_name
        if os.path.isfile(sub_folder_name):
            continue
            
        device_sn = sub_folder_name
        result_path = os.path.join(ws_storage_folder, device_sn, result_folder_name)
        result_full_path = os.path.join(result_path, csv_file_name)
        if not os.path.exists(result_full_path):
            print('\nCannot find the file {}.'
                  '\nPlease make sure this file is in located folder {}.'
                  '\nThen start this program again.'.format(csv_file_name,result_path))
            break
        else:
            print("  {}".format(result_full_path))
    
            # ---------- Start to convert CSV into EXCEL or CSV ----------
            # collect data from input file
            rows = ReadCSVasList(result_full_path)
#            print rows[row_number][column_number]
            columns = map(list,zip(*rows))
#            print columns

            if header == []:
                header = columns[0][1:]
                header.insert(0, 'SN')
#                print header
            
            values = columns[2][1:]
            values.insert(0, device_sn)
#            print values

            results.append(values) 
            # ---------- End to convert CSV into EXCEL or CSV ----------
#    print results

    # copy content only to output file
    WriteListToCSV(collect_full_path, results, header)

    if os.path.exists(collect_full_path):
        print('\nSuccess: {}'.format(collect_full_path))
    else:
        print('\nFailure: {}'.format(collect_full_path))
    
    print('\nCollect Done.')
