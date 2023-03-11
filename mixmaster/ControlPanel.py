# This file is part of Cantera. See License.txt in the top-level directory or
# at http://www.cantera.org/license.txt for license and copyright information.

from __future__ import print_function

#import datawindow
#import filewindow
from types import *
import sys

if sys.version_info[0] == 3:
    import tkinter as tk
    from tkinter.scrolledtext import ScrolledText
else:
    import Tkinter as tk
    from ScrolledText import ScrolledText



class ControlWindow(tk.Frame):
    def __init__(self, title, master=None):
        tk.Frame.__init__(self, master)
        self.app = master
        self.grid(row=0, column=0, sticky=tk.E + tk.W + tk.N + tk.S)
        self.master.title(title)

    def addButtons(self, label, funcs):
        self.buttonholder = tk.Frame(self, relief=tk.FLAT, bd=2)
        self.buttonholder.pack(side=tk.TOP, anchor=tk.W)
        b = tk.Label(self.buttonholder, text=label)
        b.pack(side=tk.LEFT, fill=tk.X)
        for f in funcs:
            b = tk.Button(self.buttonholder, text=f[0], command=f[1], padx=1, pady=1)
            b.pack(side=tk.LEFT, fill=tk.X)

    def disableButtons(self, *buttons):
        for button in self.buttonholder.slaves():
            if button.cget('text') in buttons:
                try:
                    button.config(state=tk.DISABLED)
                except:
                    pass

    def enableButtons(self, *buttons):
        for button in self.buttonholder.slaves():
            if button.cget('text') in buttons:
                try:
                    button.config(state=tk.NORMAL)
                except:
                    pass

    def newFrame(self, label, var):
        fr = tk.Frame(self, relief=tk.RIDGE, bd=2)
        fr.pack(side=tk.TOP, fill=tk.X)
        c = tk.Checkbutton(fr, variable=var)
        c.pack(side=tk.LEFT, fill=tk.X)
        b = tk.Label(fr, text=label, foreground="NavyBlue")
        b.pack(side=tk.LEFT, fill=tk.X)
        return fr

    # creates a new Toplevel object
    # options:  transient=<callback for window close>,
    #                      placement=(<screen x-coord>, <screen y-coord>)
    def newWindow(self, master, title, **options):
        new = tk.Toplevel(master)
        new.title(title)
        #new.config(takefocus=0)
        if 'transient' in options.keys():
            new.transient(master)
            if options['transient']:
                new.protocol('WM_DELETE_WINDOW', options['transient'])
        if 'placement' in options.keys():
            new.geometry("+%d+%d" % tuple(options['placement']))
        return new

    # routes mouse and keyboard events to the window and
    # waits for it to close before returning
    def makemodal(self, window):
        window.focus_set()
        window.grab_set()
        window.wait_window()
        return

    def PlotMenu(self, fr, label, funcs):
        filebutton = tk.Menubutton(fr, text=label, padx=3, pady=1)
        filebutton.pack(side=tk.LEFT)
        filemenu = tk.Menu(filebutton, tearoff=tk.TRUE)
        i = 0
        for f in funcs:
            filemenu.add_command(label=f[0], command=f[1])
            i += 1
        filebutton['menu'] = filemenu
        return filemenu


def testevent(event):
    print('event ', event.value)


def make_menu(name, menubar, lst):
    nc = len(name)
    button = tk.Menubutton(menubar, text=name, width=nc + 4, padx=3, pady=1)
    button.pack(side=tk.LEFT)
    menu = tk.Menu(button, tearoff=tk.FALSE)
    for entry in lst:
        add_menu_item(menu, entry)
    button['menu'] = menu
    return button


def add_menu_item(menu, entry):
    if entry == 'separator':
        menu.add_separator({})
    elif isinstance(entry, list):
        for num in entry:
            menu.entryconfig(num, state=tk.DISABLED)
    elif not isinstance(entry[1], list):
        if len(entry) == 2 or entry[2] == 'command':
            menu.add_command(label=entry[0], command=entry[1])
        elif entry[2] == 'check':
            entry[3].set(0)
            if len(entry) >= 5:
                val = entry[4]
            else:
                val = 1
            menu.add_checkbutton(label=entry[0], command=entry[1],
                                 variable=entry[3], onvalue=val)
    else:
        submenu = make_menu(entry[0], menu, entry[1])
        menu.add_cascade(label=entry[0], menu=submenu)


def menuitem_state(button, *statelist):
    for menu in button.children.keys():
        if isinstance(button.children[menu], tk.Menu):
            for (commandnum, onoff) in statelist:
                if onoff == 0:
                    button.children[menu].entryconfig(commandnum, state=tk.DISABLED)
                if onoff == 1:
                    button.children[menu].entryconfig(commandnum, state=tk.NORMAL)
        else:
            pass


class ArgumentWindow(tk.Toplevel):
    def __init__(self, sim, **options):
        tk.Toplevel.__init__(self, sim.cwin)
        self.resizable(tk.FALSE, tk.FALSE)
        self.protocol("WM_DELETE_WINDOW", lambda: 0)  #self.cancelled)
        self.transient(sim.cwin)
        if 'placement' in options.keys():
            self.geometry("+%d+%d" % tuple(options['placement']))
        self.title('Thermal Model Initialization')
        self.sim = sim

        self.make_options()

        buttonframe = tk.Frame(self)
        buttonframe.pack(side=tk.BOTTOM)
        b1 = tk.Button(buttonframe, text='OK', command=self.callback)
        b1.pack(side=tk.LEFT)
        #b2=Button(buttonframe, text='Cancel', command=self.cancelled)
        #b2.pack(side=LEFT)
        self.bind("<Return>", self.callback)
        #self.bind("<Escape>", self.cancelled)

        self.initial_focus = self
        self.initial_focus.focus_set()
        #self.wait_window(self)

    def make_options(self):
        pass
        ###  must override this function    ###
        ###  with the entry forms           ###
        ###  be sure to use pack or a       ###
        ###      frame that is packed into self ###

    def getArguments(self):
        pass
        ###  must override this function  ###
        ###  with the validation checking ###
        ###  must return None if error,   ###
        ###  and non_null if ok                   ###

    def callback(self, event=None):
        g = self.getArguments()
        if not g:
            self.initial_focus.focus_set()
            return
        self.withdraw()
        self.update_idletasks()

        self.assign(g)
        self.cancelled()

    def assign(self, obj):
        pass
        ###  must override this function  ###
        ###  to do the assignment in sim  ###

    def cancelled(self, event=None):
        self.sim.cwin.focus_set()
        self.destroy()


if __name__ == '__main__':
    t = tk.Tk()
    ControlWindow(t).mainloop()
