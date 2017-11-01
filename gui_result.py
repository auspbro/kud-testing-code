#!/usr/bin/python
# -*- coding: UTF-8 -*-

from tkinter import *
import tkFont
import yaml
import os
import sys
import glob
import csv
import environ as env


fields = ['Connect', 'SerialNumber']
fail_bg_color = '#820427'
fail_fg_color = 'White'
pass_bg_color = '#9bc8a5'
pass_fg_color = 'black'


def GetSerialNumber():
    settings = {}
    with open('settings.yml', 'r') as infile:
        settings = yaml.load(infile)
        infile.close()
    return settings['SN']

def fetch(entries):
    '''
    for entry in entries:
        field = entry[0]
        text  = entry[1].get().strip()
        print('%s: "%s"' % (field, text))
    '''
    quit()

def makeform(root, fields):
    FontConf = tkFont.Font(family='Times', size=12)#, weight=tkFont.BOLD)
    entries = []
    mEntries = []
    for n, field in enumerate(fields):
        row = Frame(root)
        lab = Label(row, font=FontConf, width=16, text=field, anchor='w')
        ent = Entry(row, font=FontConf, width=18, relief=FLAT, fg=pass_fg_color, bg=pass_bg_color)
        mEnt = Entry(row, font=FontConf, width=48, relief=FLAT)#, state=DISABLED)    
        row.pack(side=TOP, fill=X, padx=1, pady=1)
        lab.pack(side=LEFT)
        ent.pack(side=LEFT, expand=YES, fill=X)
        entries.append((field, ent))
        mEnt.pack(side=RIGHT, expand=YES, fill=X)
        mEntries.append((field, mEnt))
    return (entries,mEntries)
    
if __name__ == '__main__':
    root = Tk()
    
    display_enable = 'False'
    if len(sys.argv) > 1:
        display_enable =  sys.argv[1]
        
    if len(sys.argv) <= 2:
#        print 'no argument'
        ResultDirectory = ''
        if os.path.exists(env.tester_results_folder):
            ResultDirectory = env.tester_results_folder
        else:
            SN = GetSerialNumber()
            ResultDirectory = os.path.join(env.ws_storage_folder, SN, env.result_folder_name)
        if not os.path.exists(ResultDirectory):
            print(">> Sorry, can not find folder %s <<" % ResultDirectory)
            env.print_warn("FAIL")
            quit()
    else:
        ResultDirectory = sys.argv[2]
    
    Title = Entry(root, # justify='center',
                    font = "Times 16 bold",
                    fg = "black",
                    bg = "#48a9f2")
    Title.pack(side=TOP, padx=5, pady=5, expand=YES, fill=X)
    Title.insert(10, ResultDirectory)
    
    if not os.path.exists(env.criteria_file_full_path):
        print(">> Sorry, Can not find file %s <<" % env.criteria_file_full_path)
        env.print_warn("FAIL")
        quit()
            
    # https://stackoverflow.com/questions/3964681/find-all-files-in-a-directory-with-extension-txt-in-python
    # https://www.saltycrane.com/blog/2008/04/working-with-files-and-directories-in/
    fields = []
    result_dict = {}
    os.chdir(ResultDirectory)
    for filename in glob.glob("*.cmd"):
#        print "---- %s ----" % filename
        lines = [line.rstrip('\n') for line in open(filename)]
        lines = [w.replace('SET ', '') for w in lines]
        for line in lines:
#            print line
            items = line.strip().split('=')
            result_dict[items[0]] = items[1]
#    print result_dict

    fields = result_dict.keys()
    fields.sort() 
    
    ents,mEnts = makeform(root, fields)
    root.bind('<Return>', (lambda event, e=ents: fetch(e)))
    
    b2 = Button(root, font="Helvetica 22 bold", text='Quit', command=root.quit)
    b2.pack(side=LEFT, padx=5, pady=5, expand=YES, fill=X)
#    b1 = Button(root, font="Helvetica 22 bold", text='generate', fg='white', bg='#142e9b', command=(lambda e=ents: fetch(e)))
#    b1.pack(side=LEFT, padx=5, pady=5, expand=YES, fill=X)
    
    fail_flag = False
    csv_file = os.path.join(ResultDirectory, env.csv_file_name)
    if os.path.exists(csv_file):
        os.remove(csv_file)
    for n in range(0, len(ents)):
        ResultKey = ents[n][0]
        ResultValue = result_dict.get(ResultKey)
        ents[n][1].insert(10, ResultValue)
#        ents[n][1]['state'] = 'readonly'
        result,comment = env.judge_cvs_result(ResultDirectory,item=ResultKey,value=ResultValue)
        mEnts[n][1].insert(10, comment)
        mEnts[n][1]['state'] = 'readonly'
        if result == 'FAIL':
            ents[n][1]['bg'] = fail_bg_color
            ents[n][1]['fg'] = fail_fg_color
            fail_flag = True

    if fail_flag:
        b2['bg'] = fail_bg_color
        b2['fg'] = fail_fg_color
        b2['text'] = 'FAIL'
    else:
        b2['bg'] = pass_bg_color
        b2['fg'] = pass_fg_color
        b2['text'] = 'PASS'
        
#    print "run %s done." % sys.argv[0]
    env.print_warn("\n%s\n" % b2["text"])
    b2.focus()
    
    # screen setting
    GUI_TITLE='Parser Results'
    root.title(GUI_TITLE)
    
    root.resizable(False, False)
    root.withdraw()
    root.update_idletasks()
    x = (root.winfo_screenwidth() - root.winfo_reqwidth()) / 2
    y = (root.winfo_screenheight() - root.winfo_reqheight()) / 2
    root.geometry("+%d+%d" % (x, y))
    root.deiconify()

    # screen display
    if display_enable.lower() == 'true':
        root.mainloop()
    else:
#        print('\nParser Results Done.')
        print ''
        quit()