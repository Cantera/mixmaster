# This file is part of Cantera. See License.txt in the top-level directory or
# at http://www.cantera.org/license.txt for license and copyright information.

import sys

if sys.version_info[0] == 3:
    import tkinter as tk
else:
    import Tkinter as tk


class TransportFrame(tk.Frame):
    def show(self, i, frame, row, col):
        if self.checked[i].get():
            frame.grid(row=row, column=col, sticky=tk.N + tk.E + tk.S + tk.W)
        else:
            frame.grid_forget()

    def showcomp(self):
        self.show(0, self.top.mixfr, 8, 0)

    def showthermo(self):
        self.show(1, self.top.thermo, 7, 0)

    def __init__(self, master, top):
        self.top = top
        self.c = []
        self.checked = []
        tk.Frame.__init__(self, master)
        self.config(relief=tk.GROOVE, bd=4)
        lbl = ['multicomponent', 'mixture-averaged']
        cmds = [self.showcomp, self.showthermo]
        for i in range(2):
            self.checked.append(tk.IntVar())
            self.checked[i].set(0)
            self.c.append(tk.Checkbutton(self, text=lbl[i], variable=self.checked[i],
                                         onvalue=1, offvalue=0, command=cmds[i]))
            self.c[i].grid(column=i, row=0, sticky=tk.W + tk.N)
