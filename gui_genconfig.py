#!/usr/bin/python
# -*- coding: UTF-8 -*-

from tkinter import *
import tkFont
import yaml
        
#fields = 'Last Name', 'First Name', 'Job', 'Country'
fields = 'Connect', 'SerialNumber'
bg_colour = '#2b081d', 'White'
fg_colour = 'black', 'black'

def genconfig(entries):
    '''
    import subprocess
    connect = entries[0][1].get().strip()
    sn = entries[1][1].get().strip()

    run_command = 'python genconfig.py {} {}'.format(connect, sn)
    print run_command
    #result = subprocess.check_output('python gui_pass_fail.py', shell=False)
    result = subprocess.check_output(run_command, shell=False)
    print 'result = {}'.format(result)
    '''
    settings = {}
    with open('settings.yml', 'r') as infile:
        settings = yaml.load(infile)
        infile.close()

    settings['CONNECT'] = entries[0][1].get().strip().upper()
    if entries[1][1].get().strip() != '':
        settings['SN'] = entries[1][1].get().strip()
        with open('settings.yml', 'w') as outfile:
            yaml.dump(settings, outfile, default_flow_style=False)
            outfile.close()
    else:
        entries[1][1].insert(10, settings['SN'] )

    
def fetch(entries):
    genconfig(entries)
    for entry in entries:
        field = entry[0]
        text  = entry[1].get().strip()
        print('%s: "%s"' % (field, text))
    quit()

    
def makeform(root, fields):
    helvetica = tkFont.Font(family='Helvetica', size=20, weight=tkFont.BOLD)
    entries = []
    for n, field in enumerate(fields):
        row = Frame(root)
        lab = Label(row, font=helvetica, width=12, text=field, anchor='w')
        ent = Entry(row, font=helvetica, fg=fg_colour[n], bg=bg_colour[n])
        row.pack(side=TOP, fill=X, padx=5, pady=5)
        lab.pack(side=LEFT)
        ent.pack(side=RIGHT, expand=YES, fill=X)
        entries.append((field, ent))
    return entries

    
if __name__ == '__main__':
    root = Tk()    
    
    ents = makeform(root, fields)
    root.bind('<Return>', (lambda event, e=ents: fetch(e)))
    
#    b2 = Button(root, font=helvetica, text='Quit', command=root.quit)
#    b2.pack(side=LEFT, padx=5, pady=5)
    b1 = Button(root, font="Helvetica 22 bold", text='generate', fg='white', bg='#142e9b', command=(lambda e=ents: fetch(e)))
    b1.pack(side=LEFT, padx=5, pady=5, expand=YES, fill=X)

    ents[0][1].insert(10, "UART")
    ents[0][1]['state'] = 'readonly'

    ents[1][1].focus()

    GUI_TITLE='GenConfig'
    root.title(GUI_TITLE)

    root.resizable(False, False)
    root.withdraw()
    root.update_idletasks()
    x = (root.winfo_screenwidth() - root.winfo_reqwidth()) / 2
    y = (root.winfo_screenheight() - root.winfo_reqheight()) / 2
    root.geometry("+%d+%d" % (x, y))
    root.deiconify()
    
    root.mainloop()