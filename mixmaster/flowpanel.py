# This file is part of Cantera. See License.txt in the top-level directory or
# at http://www.cantera.org/license.txt for license and copyright information.

# functionality imports
import sys
from cantera.mixmaster import menu, newflow

if sys.version_info[0] == 3:
    import tkinter as tk
else:
    import Tkinter as tk


class App:
    def __init__(self, master):
        try:
            self.root = master.root
        except:
            self.root = master

        self.frame = tk.Frame(master)
        self.frame.grid(row=0, column=0)
        self.makemenu(self.frame)

        self.quitbutton = tk.Button(self.frame, text='Quit', command=self.frame.quit)
        self.quitbutton.grid(row=1, column=0)

        self.newbutton = tk.Button(self.frame, text='New...', command=self.notyet)
        self.newbutton.grid(row=1, column=1)

    def notyet(self):
        print('not yet!')

    def newflow(self):
        n = newflow.NewFlowDialog(self.root)

    def makemenu(self, frame):
        self.menubar = tk.Frame(frame, relief=tk.FLAT, bd=0)
        self.menubar.grid(row=0, column=0)

        self.filemenu = menu.make_menu('File', self.menubar,
                                  [('New...', self.newflow),
                                   ('Open...', self.notyet),
                                   ('Save As...', self.notyet),
                                   'separator',
                                   ('Exit', frame.quit),
                                   []
                                   ])



root = tk.Tk()
app = App(root)
root.mainloop()
