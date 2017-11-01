#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
from Tkinter import *
import tkFont
from tkMessageBox import *

# https://www.tcl.tk/man/tcl8.4/TkCmd/colors.htm
# http://blog.csdn.net/bnanoou/article/details/38434443#

WINDOW_SIZE='400x600'
GUI_TITLE='Press PASS or FAIL'
PhotoName = '..\photo\Motor.gif'


counter = 0 
def counter_label(label):
    def count():
        global counter
        counter += 1
        label.config(text=str(counter))
        label.after(1000, count)
        '''
        if counter == 3600:
            print("FAIL")
            quit()
        '''
    count()


def printCoords(event):
    print 'clicked = ', event.x, event.y
    print 'event.char = ', repr(event.char) # pressed
    print 'event.keycode = ', repr(event.keycode)
    print 'event.keysym = ', event.keysym
    print 'event.type = ', event.type

'''
def handler(event, a, b, c):
    print (event)
    print ("handler", a, b, c )

def handleradaptor(fun, **kwds):
    return lambda event,fun=fun,kwds=kwds: fun(event, **kwds)
'''


class App:
    def __init__(self, master=None):
        self.Pass = 'PASS'
        self.Fail = 'FAIL'
        self.result = self.Fail
#        self.photoname = '..\photo\Motor.gif'
        
        frame = Frame(master,bg = "black")       
        frame.pack(side = TOP)
        
        helvetica80 = tkFont.Font(family='Helvetica', size=80, weight=tkFont.BOLD)
        
        self.TitleLabel = Label(frame, 
                        font = "Helvetica 22 bold",
                        fg = "white",
                        bg = "black",
                        compound = CENTER)
        self.TitleLabel.pack(side = TOP)
#        counter_label(self.TitleLabel)

        global PhotoName
        if os.path.exists(PhotoName):
#        if os.path.exists(self.photoname):
            self.PhotoLabel = Label(frame, bg='white', justify='center')
#            self.photo = PhotoImage(file = self.photoname)
            self.photo = PhotoImage(file = PhotoName)
            self.PhotoLabel["compound"] = "bottom"
            self.PhotoLabel["image"] = self.photo
            self.PhotoLabel.pack(padx=1, pady=1, fill=BOTH, expand=1)

        self.failbtn = Button(frame,
                        font = helvetica80,
                        text = self.Fail,
                        fg = "black",
                        bg = "Red",
                        width = 6,
                        command = lambda:self.btn_command(self.failbtn))

        self.failbtn.bind("<Key>", self.btn_key_event)
        self.failbtn.pack(side = LEFT)
        self.failbtn.focus_set()
        
        self.passbtn = Button(frame,
                        font = helvetica80,
                        text = self.Pass,
                        fg = "black",
                        bg = "lawn green",
                        width = 6,
                        command = lambda:self.btn_command(self.passbtn))
        
        self.passbtn.bind("<Key>", self.btn_key_event)
        self.passbtn.pack(side = RIGHT)
        
#        self.passbtn.bind("<Button-1>", printCoords)
#        self.passbtn.bind("<Key>", handleradaptor(handler, a=1, b=2, c=3) )
        

    def on_exit(self):
        # "Do you want to quit the application?"
        if askyesno('Exit', 'Really quit?'):
            print("FAIL")
            quit()


    def btn_command(self, btn):
#        print(btn["text"])
        self.result = btn["text"]
        print( self.result )
#        btn.configure(state=DISABLED, background='cadetblue')
        quit()

    
    def btn_key_event(self, event=None):
        choice_fg_color = "white"
        choice_bg_color = "cadetblue"       
        if event.keycode == 39 or event.keycode == 89 or event.keycode == 80: # Right=39, Y=89, P=80
            self.result = self.Pass
            self.passbtn.focus_set()
            self.passbtn.configure(fg = choice_fg_color, bg = choice_bg_color)
            self.failbtn.configure(fg = "black", bg= "Red")
            if event.keycode != 39:
                print( self.result )
                quit()
        elif event.keycode == 37 or event.keycode == 78 or event.keycode == 70: # Left=37, N=78, F=70
            self.result = self.Fail
            self.failbtn.focus_set()
            self.passbtn.configure(fg = "black", bg = "lawn green")
            self.failbtn.configure(fg = choice_fg_color, bg = choice_bg_color)
            if event.keycode != 37:
                print( self.result )
                quit()
        elif event.keycode == 9: # Tab=9
            self.result = event.widget['text']
            if self.result == self.Pass:
                self.passbtn.configure(fg = "black", bg = "lawn green")
                self.failbtn.configure(fg = choice_fg_color, bg = choice_bg_color)
                self.result = self.Fail
            elif self.result == self.Fail:
                self.failbtn.configure(fg = "black", bg= "Red")
                self.passbtn.configure(fg = choice_fg_color, bg = choice_bg_color)
                self.result = self.Pass
        if event.keycode == 13: # Return_key=13
            print( self.result )
            quit()      


if __name__ == '__main__':   
    root = Tk()

    if len(sys.argv) >= 3:
        if os.path.exists(sys.argv[2]):
            PhotoName = sys.argv[2]   
    
    app = App(root)

    if len(sys.argv) >= 2:
        app.TitleLabel.config(text=sys.argv[1])
    else:
        counter_label(app.TitleLabel)     

    root.protocol("WM_DELETE_WINDOW", app.on_exit)
    
    root.title(GUI_TITLE)

    #root.geometry(WINDOW_SIZE)
    root.resizable(False, False)
    root.withdraw()
    root.update_idletasks()
    x = (root.winfo_screenwidth() - root.winfo_reqwidth()) / 2
    y = (root.winfo_screenheight() - root.winfo_reqheight()) / 2
    root.geometry("+%d+%d" % (x, y))
    root.deiconify()
    
    root.mainloop()