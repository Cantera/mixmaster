#
#  function getElements displays a periodic table, and returns a list of
#  the selected elements
#

# This file is part of Cantera. See License.txt in the top-level directory or
# at http://www.cantera.org/license.txt for license and copyright information.

import string
import sys

import cantera as ct

if sys.version_info[0] == 3:
    import tkinter as tk
else:
    import Tkinter as tk


# (row,column) positions in the periodic table
_pos = {'H':(1,1), 'He':(1,18),
        'Li':(2,1), 'Be':(2,2),
        'B':(2,13), 'C':(2,14), 'N':(2,15), 'O':(2,16), 'F':(2,17), 'Ne':(2,18),
        'Na':(3,1), 'Mg':(3,2),
        'Al':(3,13), 'Si':(3,14), 'P':(3,15), 'S':(3,16), 'Cl':(3,17), 'Ar':(3,18),
        'K':(4,1), 'Ca':(4,2),
        'Sc':(4,3), 'Ti':(4,4), 'V':(4,5), 'Cr':(4,6), 'Mn':(4,7), 'Fe':(4,8),
        'Co':(4,9), 'Ni':(4,10), 'Cu':(4,11), 'Zn':(4,12),
        'Ga':(4,13), 'Ge':(4,14), 'As':(4,15), 'Se':(4,16), 'Br':(4,17), 'Kr':(4,18),
        'Rb':(5,1), 'Sr':(5,2),
        'Y':(5,3), 'Zr':(5,4), 'Nb':(5,5), 'Mo':(5,6), 'Tc':(5,7), 'Ru':(5,8),
        'Rh':(5,9), 'Pd':(5,10), 'Ag':(5,11), 'Cd':(5,12),
        'In':(5,13), 'Sn':(5,14), 'Sb':(5,15), 'Te':(5,16), 'I':(5,17), 'Xe':(5,18)
        }


class PeriodicTable(tk.Frame):
    def __init__(self, master, selected=[]):
        tk.Frame.__init__(self, master)
        self.master = master
        self.control = tk.Frame(self)
        self.control.config(relief=tk.GROOVE, bd=4)
        tk.Button(self.control, text='Display', command=self.show).pack(fill=tk.X, pady=3, padx=10)
        tk.Button(self.control, text='Clear', command=self.clear).pack(fill=tk.X, pady=3, padx=10)
        tk.Button(self.control, text='  OK  ', command=self.get).pack(side=tk.BOTTOM, fill=tk.X,
                                                                      pady=3, padx=10)
        tk.Button(self.control, text='Cancel', command=self.master.quit).pack(side=tk.BOTTOM, fill=tk.X,
                                                                              pady=3, padx=10)
        self.entries = tk.Frame(self)
        self.entries.pack(side=tk.LEFT)
        self.control.pack(side=tk.RIGHT, fill=tk.Y)
        self.c = {}
        self.element = {}
        self.selected = selected
        n = 0
        ncol = 8
        for el in _pos.keys():
            self.element[el] = tk.Frame(self.entries)
            self.element[el].config(relief=tk.GROOVE, bd=4, bg=self.color(el))
            self.c[el] = tk.Button(self.element[el], text=el, bg=self.color(el), width=3, relief=tk.FLAT)
            self.c[el].pack()
            self.c[el].bind("<Button-1>", self.setColors)
            self.element[el].grid(row=_pos[el][0] - 1, column=_pos[el][1] - 1,
                                  sticky=tk.W + tk.N + tk.E + tk.S)
            n += 1

        label_text = 'select the elements to be included, and then press OK.\n' \
                     'To view the properties of the selected elements, press Display '
        tk.Label(self.entries, text=label_text).grid(row=0, column=2, columnspan=10, sticky=tk.W)

    def select(self, el):
        e = string.capitalize(el)
        self.c[e]['relief'] = tk.RAISED
        self.c[e]['bg'] = self.color(e, sel=1)

    def deselect(self, el):
        e = string.capitalize(el)
        self.c[e]['relief'] = tk.FLAT
        self.c[e]['bg'] = self.color(e, sel=0)

    def selectElements(self, ellist):
        for el in ellist:
            ename = el
            self.select(ename)

    def setColors(self, event):
        el = event.widget['text']
        if event.widget['relief'] == tk.RAISED:
            event.widget['relief'] = tk.FLAT
            back = self.color(el, sel=0)
        elif event.widget['relief'] == tk.FLAT:
            event.widget['relief'] = tk.RAISED
            back = self.color(el, sel=1)
        event.widget['bg'] = back

    def color(self, el, sel=0):
        _normal = ['#88dddd', '#dddd88', '#dd8888']
        _selected = ['#aaffff', '#ffffaa', '#ffaaaa']
        row, column = _pos[el]
        if sel:
            list = _selected
        else:
            list = _normal
        if column < 3:
            return list[0]
        elif column > 12:
            return list[1]
        else:
            return list[2]

    def show(self):
        elnames = _pos.keys()
        elnames.sort()
        selected = []
        for el in elnames:
            if self.c[el]['relief'] == tk.RAISED:
                selected.append(ct.periodicTable[el])
        showElementProperties(selected)

    def get(self):
        self.selected = []
        names = _pos.keys()
        names.sort()
        for el in names:
            if self.c[el]['relief'] == tk.RAISED:
                self.selected.append(ct.periodicTable[el])
        #self.master.quit()'
        self.master.destroy()

    def clear(self):
        for el in _pos.keys():
            self.c[el]['bg'] = self.color(el, sel=0)
            self.c[el]['relief'] = tk.FLAT


class ElementPropertyFrame(tk.Frame):
    def __init__(self, master, ellist):
        tk.Frame.__init__(self, master)
        n = 1
        ellist.sort()
        tk.Label(self, text='Name').grid(column=0, row=0, sticky=tk.W + tk.S, padx=10, pady=10)
        tk.Label(self, text='Atomic \nNumber').grid(column=1, row=0, sticky=tk.W + tk.S, padx=10, pady=10)
        tk.Label(self, text='Atomic \nWeight').grid(column=2, row=0, sticky=tk.W + tk.S, padx=10, pady=10)
        for el in ellist:
            tk.Label(self, text=el.name).grid(column=0, row=n, sticky=tk.W, padx=10)
            tk.Label(self, text=repr(el.atomicNumber)).grid(column=1, row=n, sticky=tk.W, padx=10)
            tk.Label(self, text=repr(el.atomicWeight)).grid(column=2, row=n, sticky=tk.W, padx=10)
            n += 1


# utility functions
def getElements(ellist=None):
    master = tk.Toplevel()
    master.title('Periodic Table of the Elements')
    t = PeriodicTable(master)
    if ellist:
        t.selectElements(ellist)
    t.pack()
    t.focus_set()
    t.grab_set()
    t.wait_window()
    try:
        master.destroy()
    except tk.TclError:
        pass
    return t.selected


# display table of selected element properties in a window
def showElementProperties(ellist):
    m = tk.Tk()
    m.title('Element Properties')
    elem = []
    ElementPropertyFrame(m, ellist).pack()


if __name__ == "__main__":
    print(getElements())
