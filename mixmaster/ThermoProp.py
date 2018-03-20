# This file is part of Cantera. See License.txt in the top-level directory or
# at http://www.cantera.org/license.txt for license and copyright information.

import sys

from UnitChooser import UnitVar

if sys.version_info[0] == 3:
    import tkinter as tk
else:
    import Tkinter as tk


_tv = ['Temperature','Internal Energy','Enthalpy']
_pv = ['Pressure', 'Density']


def badpair(a, b):
    if a.name in _tv:
        if not b.name not in _pv:
            return 1
    else:
        if not b.name in _tv:
            return 1


class ThermoProp:
    def __init__(self, master, thermoframe, row, name, value, units, defaultunit=0):
        self.value = tk.DoubleVar()
        self.thermoframe = thermoframe
        self.entry = UnitVar(master, units, defaultunit)
        self.entry.grid(column=1, row=row, sticky=tk.W)
        self.entry.v.config(state=tk.DISABLED, bg='lightgray')
        self.checked = tk.IntVar()
        self.checked.set(0)
        self.name = name
        self.c = tk.Checkbutton(master, text=name, variable=self.checked,
                                onvalue=1, offvalue=0, command=self.check)
        self.c.grid(column=0, row=row, sticky=tk.W + tk.N)

    def check(self):
        if self == self.thermoframe.last1:
            self.checked.set(1)
            return
        elif self == self.thermoframe.last2:
            self.checked.set(1)
            self.thermoframe.last2 = self.thermoframe.last1
            self.thermoframe.last1 = self
            return
#               elif badpair(self, self.thermoframe.last1):
#                       self.checked.set(0)
#                       return

        self._check()
        self.thermoframe.last2.checked.set(0)
        self.thermoframe.last2._check()
        self.thermoframe.last2 = self.thermoframe.last1
        self.thermoframe.last1 = self

    def _check(self):
        if self.isChecked():
            self.entry.v.config(state=tk.NORMAL, bg='white')
        else:
            self.entry.v.config(state=tk.DISABLED, bg='lightgray')

    def isChecked(self):
        return self.checked.get()

    def set(self, value):
        self.entry.set(value)

    def get(self):
        return self.entry.get()
