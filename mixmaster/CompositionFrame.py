# This file is part of Cantera. See License.txt in the top-level directory or
# at http://www.cantera.org/license.txt for license and copyright information.

import sys
import numpy as np

from cantera import *
from SpeciesInfo import SpeciesInfo
#from KineticsFrame import KineticsFrame

if sys.version_info[0] == 3:
    import tkinter as tk
else:
    import Tkinter as tk

_CUTOFF = 1.e-15
_ATOL = 1.e-15
_RTOL = 1.e-7


class CompFrame(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.config(relief=tk.FLAT, bd=4)
        self.top = self.master.top
        self.controls = tk.Frame(self)
        self.hide = tk.IntVar()
        self.hide.set(0)
        self.comp = tk.IntVar()
        self.comp.set(0)
        self.controls.grid(column=1, row=0, sticky=tk.W + tk.E + tk.N)
        self.makeControls()
        mf = self.master

    def makeControls(self):
        tk.Radiobutton(self.controls, text='Moles', variable=self.comp, value=0,
                       command=self.show).grid(column=0, row=0, sticky=tk.W)
        tk.Radiobutton(self.controls, text='Mass', variable=self.comp, value=1,
                       command=self.show).grid(column=0, row=1, sticky=tk.W)
        tk.Radiobutton(self.controls, text='Concentration', variable=self.comp, value=2,
                       command=self.show).grid(column=0, row=2, sticky=tk.W)
        tk.Button(self.controls, text='Clear', command=self.zero).grid(column=0, row=4,
                                                                       sticky=tk.W + tk.E)
        tk.Button(self.controls, text='Normalize', command=self.norm).grid(column=0, row=5,
                                                                           sticky=tk.W + tk.E)
        tk.Checkbutton(self.controls, text='Hide Missing\nSpecies',
                       variable=self.hide, onvalue=1,
                       offvalue=0, command=self.master.redo).grid(column=0, row=3, sticky=tk.W)

    def norm(self):
        mf = self.master
        mf.update()

        data = mf.comp
        sum = 0.0
        for sp in data:
            sum += sp
        for i in range(len(mf.comp)):
            mf.comp[i] /= sum
        self.show()

    def set(self):
        c = self.comp.get()
        mix = self.top.mix
        mf = self.master
        g = mix.g
        if c == 0:
            mix.setMoles(mf.comp)
        elif c == 1:
            mix.setMass(mf.comp)
        elif c == 2:
            pass
        self.top.thermo.setState()
        self.top.kinetics.show()

    def show(self):
        mf = self.master
        mf.active = self
        c = self.comp.get()
        mix = self.top.mix
        g = mix.g
        if c == 0:
            mf.var.set("Moles")
            #mf.data = spdict(mix.g, mix.moles())
            mf.comp = mix.moles()
        elif c == 1:
            mf.var.set("Mass")
            #mf.data = spdict(mix.g,mix.mass())
            mf.comp = mix.mass()
        elif c == 2:
            mf.var.set("Concentration")
            mf.comp = g.concentrations
            #mf.data = spdict(mix,mix,mf.comp)

        for s in mf.variable.keys():
            try:
                k = g.species_index(s)
                if mf.comp[k] > _CUTOFF:
                    mf.variable[s].set(mf.comp[k])
                else:
                    mf.variable[s].set(0.0)
            except:
                pass

    def zero(self):
        mf = self.master
        mf.comp *= 0.0
        self.show()


class MixtureFrame(tk.Frame):
    def __init__(self, master, top):
        tk.Frame.__init__(self, master)
        self.config(relief=tk.GROOVE, bd=4)
        self.top = top
        self.top.mixframe = self
        self.g = self.top.mix.g
        #self.scroll = Scrollbar(self)
        self.entries = tk.Frame(self)
        #self.scroll.config(command=self.entries.xview)
        #self.scroll.grid(column=0,row=1)
        self.var = tk.StringVar()
        self.var.set("Moles")
        self.comp = np.array(self.top.mix.moles())
        self.names = self.top.mix.speciesNames()
        self.nsp = len(self.names)
        #self.data = self.top.mix.moleDict()
        self.makeControls()
        self.makeEntries()
        self.entries.bind('<Double-l>', self.minimize)
        self.ctype = 0
        self.newcomp = 0

    def makeControls(self):
        self.c = CompFrame(self)
        #self.k = KineticsFrame(self)
        self.active = self.c
        self.c.grid(column=1, row=0, sticky=tk.E + tk.W + tk.N + tk.S)
        #self.k.grid(column=2,row=0,sticky=tk.E + tk.W + tk.N + tk.S)

    def update(self):
        self.newcomp = 0
        for s in self.variable.keys():
            k = self.g.species_index(s)
            current = self.comp[k]
            val = self.variable[s].get()
            dv = abs(val - current)
            if dv > _RTOL * abs(current) + _ATOL:
                self.comp[k] = val
                self.newcomp = 1

    def show(self):
        self.active.show()
##              for k in range(self.nsp):
##                      sp = self.names[k]
##                      if self.comp[k] > _CUTOFF:
##                              self.variable[sp].set(self.comp[k])
##                      else:
##                              self.variable[sp].set(0.0)

    def redo(self):
        self.update()
        self.entries.destroy()
        self.entries = tk.Frame(self)
        self.makeEntries()

    def minimize(self, Event=None):
        self.c.hide.set(1)
        self.redo()
        self.c.grid_forget()
        self.entries.bind("<Double-1>", self.maximize)

    def maximize(self, Event=None):
        self.c.hide.set(0)
        self.redo()
        self.c.grid(column=1, row=0, sticky=tk.E + tk.W + tk.N + tk.S)
        self.entries.bind("<Double-1>", self.minimize)

    def up(self, x):
        self.update()
        if self.newcomp:
            self.c.set()
            self.c.show()
            self.top.update()
            #thermo.showState()
            #self.top.kinetics.show()

    def makeEntries(self):
        self.entries.grid(row=0, column=0, sticky=tk.W + tk.N + tk.S + tk.E)
        self.entries.config(relief=tk.FLAT, bd=4)
        DATAKEYS = self.top.species
        self.variable = {}

        n = 0
        ncol = 3
        col = 0
        row = 60

        equil = 0
        if self.top.thermo:
            equil = self.top.thermo.equil.get()

        for sp in DATAKEYS:
            s = sp  # self.top.species[sp]
            k = s.index
            if row > 25:
                row = 0
                col += 2
                l = tk.Label(self.entries, text='Species')
                l.grid(column=col, row=row, sticky=tk.E + tk.W)
                e1 = tk.Entry(self.entries)
                e1.grid(column=col+1, row=row, sticky=tk.E + tk.W)
                e1['textvariable'] = self.var
                e1.config(state=tk.DISABLED)
                e1.config(bg='lightyellow', relief=tk.RIDGE)
                row += 1

            spname = s.name
            val = self.comp[k]
            if not self.c.hide.get() or val:
                showit = 1
            else:
                showit = 0

            l = SpeciesInfo(self.entries, species=s, text=spname, relief=tk.FLAT,
                            justify=tk.RIGHT, fg='darkblue')
            entry1 = tk.Entry(self.entries)
            self.variable[spname] = tk.DoubleVar()
            self.variable[spname].set(self.comp[k])
            entry1['textvariable'] = self.variable[spname]
            entry1.bind('<Any-Leave>', self.up)
            if showit:
                l.grid(column=col, row=row, sticky=tk.E)
                entry1.grid(column=col + 1, row=row)
                n += 1
                row += 1
            if equil == 1:
                entry1.config(state=tk.DISABLED, bg='lightgray')
##                 if self.c.hide.get():
##                  b=Button(self.entries, height=1, command=self.maximize)
##              else:
##                  b=Button(self.entries, command=self.minimize)
##                 b.grid(column=col, columnspan=2, row=row + 1)
