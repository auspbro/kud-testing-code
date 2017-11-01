#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""Demo based on the demo mclist.tcl included with tk source distribution."""

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkFont

import re

split_symbol = '|'

settings_content = ""

case_columns = ("name", "instructions")
case_data = [
    ("ReImgInf", "Read Image information"),
    ("ReWBTMAC", "Read Wi-Fi and BT Address"),
    ]

tree_columns = ("key", "value")
tree_data = [
    ("Argentina",      "Buenos Aires",     "ARS"),
    ("Australia",      "Canberra",         "AUD"),
    ("Brazil",         "Brazilia",         "BRL"),
    ("Canada",         "Ottawa",           "CAD"),
    ("China",          "Beijing",          "CNY"),
    ("France",         "Paris",            "EUR"),
    ("Germany",        "Berlin",           "EUR"),
    ("India",          "New Delhi",        "INR"),
    ("Italy",          "Rome",             "EUR"),
    ("Japan",          "Tokyo",            "JPY"),
    ("Mexico",         "Mexico City",      "MXN"),
    ("Russia",         "Moscow",           "RUB"),
    ("South Africa",   "Pretoria",         "ZAR"),
    ("United Kingdom", "London",           "GBP"),
    ("United States",  "Washington, D.C.", "USD")
    ]

def sortby(tree, col, descending):
    """Sort tree contents when a column is clicked on."""
    # grab values to sort
    data = [(tree.set(child, col), child) for child in tree.get_children('')]

    # reorder data
    data.sort(reverse=descending)
    for indx, item in enumerate(data):
        tree.move(item[1], '', indx)

    # switch the heading so that it will sort in the opposite direction
    tree.heading(col,
        command=lambda col=col: sortby(tree, col, int(not descending)))
        
class App(object):
    def __init__(self):
        self.tree = None
        self._setup_widgets()
#        self._build_tree()

    def _setup_widgets(self):
#        '''
        self.msg = ttk.Label(wraplength="4i", justify="left", anchor="nw",
            padding=(10, 2, 10, 6),
            text=("Ttk is the new Tk themed widget set. One of the widgets it "
                  "includes is a tree widget, which can be configured to "
                  "display multiple columns of informational data without "
                  "displaying the tree itself. This is a simple way to build "
                  "a listbox that has multiple columns. Clicking on the "
                  "heading for a column will sort the data by that column. "
                  "You can also change the width of the columns by dragging "
                  "the boundary between them."))
        self.msg['text'] = settings_content
        self.msg.pack(fill='x')
#        '''

        container = ttk.Frame()
        container.pack(fill='both', expand=True)
               
        self.tree = ttk.Treeview(columns=tree_columns, selectmode="extended")
        vsb = ttk.Scrollbar(orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(column=0, row=2, sticky='nsew', in_=container)
        vsb.grid(column=1, row=2, sticky='ns', in_=container)
#        hsb.grid(column=0, row=3, sticky='ew', in_=container)

        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(0, weight=1)
        
        helvetica = tkFont.Font(family='Helvetica', size=10, weight=tkFont.BOLD)
        
        # search group
        self.SearchFrame = tk.Frame()
        self.SearchFrame.configure(borderwidth = 3, background = "green")
        self.SearchFrame.pack(side='top', fill='both', expand=1)
        
        self._toSearch = tk.StringVar()
        self.entry = tk.Entry(self.SearchFrame, textvariable=self._toSearch, background="#9fcceb", font=helvetica)
        self._toSearch.set( "" )
        self.entry.pack(side='left', fill='both', expand=1)
        self.entry.focus()
        
#        '''
        self.number = tk.StringVar()
        self.chosen = ttk.Combobox(self.SearchFrame, width=12, textvariable=self.number)
        self.chosen['values'] = tree_columns
        self.chosen.pack(side='left', fill='both', expand=1)
        self.chosen.current(0)
#        self.chosen.bind('"<<ComboboxSelected>>',  lambda _: None)
#        '''

        self.button = tk.Button(self.SearchFrame, text='Search', fg="white", bg="black", font=helvetica, command=self.OnSearch)
        self.button.pack(side='left', fill='both', expand=1)
        
        self.tree.bind('<Double-1>', self.OnDoubleClick_tree)
#        self.tree.bind("<<TreeviewSelect>>", self.OnClick)
  

    def OnSearch(self, item=''):
        for item in self.tree.selection():
            self.tree.selection_remove(item)
            
#        print( "you search "{}" by {}".format(self._toSearch.get().strip(), self.chosen.get()) )
        children = self.tree.get_children(item)      
        for child in children:
            text = self.tree.item(child, 'values')[self.chosen.current()]
#            print text
            if text.startswith(self._toSearch.get().strip()):
#                self.tree.selection_set(child)
                self.tree.selection_add(child)
                self.tree.focus(child)
#                return True
            else:
                self.tree.selection_remove(child)
                res = self.OnSearch(child)
                if res:
                    return True


    def OnDoubleClick_tree(self, event):
        row_idx = re.sub('I00','',str(self.tree.identify_row(self.tree.winfo_pointerxy()[1]-self.tree.winfo_rooty())))
        column_idx = re.sub(r'#','',str(self.tree.identify_column(self.tree.winfo_pointerxy()[0]-self.tree.winfo_rootx())))
#        print 'Row: {} & Column: {} '.format(row_idx, column_idx) 
#        curItem = self.tree.focus()
#        print self.tree.item(curItem)

        item = self.tree.identify('item',event.x,event.y)
        print("you clicked on", self.tree.item(item,"values"))
        '''
        for item in self.tree.selection():
            item_text = self.tree.item(item,"values")
            print(item_text)
        '''
#        self._toSearch.set(self.tree.item(item,"text"))
#        self.chosen.current(0)


    def _build_tree(self):
        for col in tree_columns:
            self.tree.heading(col, text=col.title(),
                command=lambda c=col: sortby(self.tree, c, 0))

        for item in case_data:
            root = []
            if item.find(split_symbol) != -1:
                root = item.split(split_symbol)
                parent = self.tree.insert('', 'end', text=root[0], open=True, values=(root[1].strip(),''))
            
                for column_data in tree_data:
                    column_data = column_data.split(' ')
                    if root[0].strip() == column_data[0].strip():
                        self.tree.insert(parent, 'end', values=(column_data[1], column_data[2]), tags=('ttk', 'simple'))

                        
def get_keys(dl, keys_list):
    '''
    result = []
    get_keys(tree_data, result)
    print tree_data
    '''
    if isinstance(dl, dict):
        keys_list += dl.keys()
        map(lambda x: get_keys(x, keys_list), dl.values())
    elif isinstance(dl, list):
        map(lambda x: get_keys(x, keys_list), dl)

        
class DictQuery(dict):
    def get(self, path, default = None):
        keys = path.split("/")
        val = None

        for key in keys:
            if val:
                if isinstance(val, list):
                    val = [ v.get(key, default) if v else None for v in val]
                else:
                    val = val.get(key, default)
            else:
                val = dict.get(self, key, default)

            if not val:
                break;

        return val

        
def run_test(idx):
    print TestCaseTab[idx].test_id,">>"
    Logger.append_test(TestCaseTab[idx].test_id)
    TestCaseTab[idx].pre()
    def on_compelet(result):
        print '[========Compelet========]: '
        print 'test_id: ', TestCaseTab[idx].test_id
        print "test_cast: ", idx
        print "test_result: ", result
        if not (type(result) is bool):
            for key, value in result.items():
                print "  ", key, "->", value
                if TestCaseTab[idx].test_id!='TestDutCompleted' or TestCaseTab[idx].test_id!='TestRecordDutID':
#                   tree_raw = "{} {} {} {} {}".format(TestCaseTab[idx].test_id, split_symbol, key, split_symbol, value)
                    tree_raw = "{} {} {}".format(TestCaseTab[idx].test_id, key, value)
                    tree_data.append(tree_raw)
#            print "\n",
        print '[========================]: '
        TestCaseTab[idx].post()

    TestCaseTab[idx].action(on_compelet) #push to work queue

'''
def main():
    root = tk.Tk()
    root.wm_title("Multi-Column List")
    root.wm_iconname("mclist")

    # optional?
#    import plastik_theme
#    plastik_theme.install('~/tile-themes/plastik/plastik')   
    
    app = App()
    root.mainloop()
    
if __name__ == "__main__":
    main()
'''
# --------------------- main ---------------------
import test_bench
import time
import sys
import os
import background_thread as job_runner
import environ as env


def settings_parser(params, filename):
    if params.has_key('ADB'):
        yield "ADB: {}, {}\n".format(params.get('ADB')['SID'], params.get('ADB')['MODE'])
    if params.has_key('SN'):
        yield "SN: {:^16}\n".format(params.get('SN'))
    if params.has_key('UART'):
        yield "UART: {}, {}\n".format(params.get('UART')['COM'], params.get('UART')['BAUD'])

    yield '\n'
    yield filename

do_SaveAsFiles_Flog = False

TestCaseTab = test_bench.TestCaseTab
Logger = test_bench.Logger
Settings = test_bench.settings
Logger.dut_id = Settings.get('SN')

settings_content = ''.join(settings_parser(Settings, sys.argv[1]))

tree_data = []
case_data = []
for idx in range(len(TestCaseTab)):
    if TestCaseTab[idx].test_id != 'TestDutCompleted':
        case_raw = "{} {} {}".format(TestCaseTab[idx].test_id, split_symbol, TestCaseTab[idx].instructions)
        case_data.append(case_raw)

if len(sys.argv) >= 3 and sys.argv[2].lower()=='true':
    do_SaveAsFiles_Flog = True

if do_SaveAsFiles_Flog:
    env.create_result_folder( Logger.dut_id )

print '[Start]'
'''
# Sakia note: no effect, really implemented in test_bench.py
TestCaseTab[1].values = sys.argv[2::]
'''

for idx in range(len(TestCaseTab)):
    try:
        run_test(idx)
        while(True):
            job = test_bench.dispatch_next()    #get on_compelet job
            if job != None:
                print
                job()
                break
            time.sleep(.1)
            #print '>',
        time.sleep(.1)
    except:
        print "main except!"
        break

print '[END]'

if do_SaveAsFiles_Flog:
    env.backup_result_folder( Logger.dut_id )

test_bench.shutdown()

root = tk.Tk()
root.wm_title("mft runner result")
root.wm_iconname("mclist")

app = App()
app._build_tree()

#root.resizable(0,0)
root.resizable(False, False)
root.withdraw()
root.update_idletasks()
x = (root.winfo_screenwidth() - root.winfo_reqwidth()) / 2
y = (root.winfo_screenheight() - root.winfo_reqheight()) / 2
root.geometry("+%d+%d" % (x, y))
root.deiconify()

root.mainloop()

#print('\nMFT Runner Done.')

