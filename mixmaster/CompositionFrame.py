# This file is part of Cantera. See License.txt in the top-level directory or
# at http://www.cantera.org/license.txt for license and copyright information.

import sys
import numpy as np

import cantera as ct
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
    '''
    The responsibilities of this class are to setup and display the information in the
    composition window that can be displayed to the user.
    
    '''
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.config(relief=tk.FLAT, bd=4)
        self.top = self.master.top
        self.controls = tk.Frame(self)
        self.hide = tk.IntVar()
        self.hide.set(0) #Initially this window is hidden
        self.comp = tk.IntVar()
        self.comp.set(0)
        self.controls.grid(column=1, row=0, sticky=tk.W + tk.E + tk.N)
        self.makeControls()

    def makeControls(self):
        tk.Radiobutton(self.controls, text='Moles', variable=self.comp, value=0,
                       command=self.show).grid(column=0, row=0, sticky=tk.W)
        tk.Radiobutton(self.controls, text='Mass', variable=self.comp, value=1,
                       command=self.show).grid(column=0, row=1, sticky=tk.W)
        tk.Radiobutton(self.controls, text='Concentration', variable=self.comp, value=2,
                       command=self.show).grid(column=0, row=2, sticky=tk.W)
        tk.Button(self.controls, text='Clear', command=self.zero).grid(column=0, row=4,
                                                                       sticky=tk.W + tk.E)
        tk.Button(self.controls, text='Normalize', command=self.normalize_species).grid(column=0, row=5,
                                                                           sticky=tk.W + tk.E)
        tk.Checkbutton(self.controls, text='Hide Unused\nSpecies',
                       variable=self.hide, onvalue=1,
                       offvalue=0, command=self.master.redo).grid(column=0, row=3, sticky=tk.W)

    def normalize_species(self):
        master_frame = self.master
        master_frame.update()

        data = master_frame.comp
        sum = 0.0
        for species in data:
            sum += species
        for i in range(len(master_frame.comp)):
            master_frame.comp[i] /= sum
        self.show()

    def set(self):
        composition = self.comp.get()
        mix = self.top.mix
        master_frame = self.master
        if composition == 0:
            mix.setMoles(master_frame.comp)
        elif composition == 1:
            mix.setMass(master_frame.comp)
        elif composition == 2:
            pass
        self.top.thermo_frame.setState()
        self.top.kinetics_frame.show()

    def show(self):
        master_frame = self.master
        master_frame.active = self
        composition = self.comp.get()
        mix = self.top.mix
        solution = mix.solution
        if composition == 0:
            master_frame.var.set("Moles")
            #mf.data = species_dict(mix.solution, mix.moles())
            master_frame.comp = mix.moles()
        elif composition == 1:
            master_frame.var.set("Mass")
            #mf.data = species_dict(mix.solution,mix.mass())
            master_frame.comp = mix.mass()
        elif composition == 2:
            master_frame.var.set("Concentration")
            master_frame.comp = solution.concentrations
            #mf.data = species_dict(mix,mix,mf.comp)

        for s in master_frame.variable.keys():
            try:
                k = solution.species_index(s)
                if master_frame.comp[k] > _CUTOFF:
                    master_frame.variable[s].set(master_frame.comp[k])
                else:
                    master_frame.variable[s].set(0.0)
            except:
                pass

    def zero(self):
        master_frame = self.master
        master_frame.comp *= 0.0
        self.show()


class MixtureFrame(tk.Frame):
    def __init__(self, master, top):
        tk.Frame.__init__(self, master)
        self.config(relief=tk.GROOVE, bd=4)
        self.top = top
        self.top.mixframe = self
        self.solution = self.top.mix.solution
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
        self.composition_frame = CompFrame(self)
        #self.k = KineticsFrame(self)
        self.active = self.composition_frame
        self.composition_frame.grid(column=1, row=0, sticky=tk.E + tk.W + tk.N + tk.S)
        #self.k.grid(column=2,row=0,sticky=tk.E + tk.W + tk.N + tk.S)

    def update(self):
        self.newcomp = 0
        for s in self.variable.keys():
            k = self.solution.species_index(s)
            current = self.comp[k]
            val = self.variable[s].get()
            dv = abs(val - current)
            if dv > _RTOL * abs(current) + _ATOL:
                self.comp[k] = val
                self.newcomp = 1

    def show(self):
        self.active.show()
        for k in range(self.nsp):
           sp = self.names[k]
           if self.comp[k] > _CUTOFF:
               self.variable[sp].set(self.comp[k])
           else:
               self.variable[sp].set(0.0)

    def redo(self):
        self.update()
        self.entries.destroy()
        self.entries = tk.Frame(self)
        self.makeEntries()

    def minimize(self, Event=None):
        self.composition_frame.hide.set(1)
        self.redo()
        self.composition_frame.grid_forget()
        self.entries.bind("<Double-1>", self.maximize)

    def maximize(self, Event=None):
        self.composition_frame.hide.set(0)
        self.redo()
        self.composition_frame.grid(column=1, row=0, sticky=tk.E + tk.W + tk.N + tk.S)
        self.entries.bind("<Double-1>", self.minimize)

    def up(self, x):
        self.update()
        if self.newcomp:
            self.composition_frame.set()
            self.composition_frame.show()
            self.top.update()
            self.top.thermo_frame.showState()
            self.top.kinetics_frame.show()

    def makeEntries(self):
        self.entries.grid(row=0, column=0, sticky=tk.W + tk.N + tk.S + tk.E)
        self.entries.config(relief=tk.FLAT, bd=4)
        DATAKEYS = self.top.species
        self.variable = {}

        n = 0
        col = 0
        row = 60

        equil = 0
        if self.top.thermo_frame:
            equil = self.top.thermo_frame.equil.get()

        for sp in DATAKEYS:
            specie_index = sp.index
            if row > 25:
                row = 0
                col += 2
                label = tk.Label(self.entries, text='Species')
                label.grid(column=col, row=row, sticky=tk.E + tk.W)
                entry = tk.Entry(self.entries)
                entry.grid(column=col+1, row=row, sticky=tk.E + tk.W)
                entry['textvariable'] = self.var
                entry.config(state=tk.DISABLED)
                entry.config(bg='lightyellow', relief=tk.RIDGE)
                row += 1

            specie_name = sp.name
            specie_composition = self.comp[specie_index]
            if not self.composition_frame.hide.get() or specie_composition:
                showit = 1
            else:
                showit = 0

            l = SpeciesInfo(self.entries, species=sp, text=specie_name, relief=tk.FLAT,justify=tk.RIGHT, fg='darkblue')
            entry1 = tk.Entry(self.entries)
            self.variable[specie_name] = tk.DoubleVar()
            self.variable[specie_name].set(self.comp[specie_index])
            entry1['textvariable'] = self.variable[specie_name]
            entry1.bind('<Any-Leave>', self.up)
            if showit:
                l.grid(column=col, row=row, sticky=tk.E)
                entry1.grid(column=col + 1, row=row)
                n += 1
                row += 1
            if equil == 1:
                entry1.config(state=tk.DISABLED, bg='lightgray')
##                 if self.composition_frame.hide.get():
##                  b=Button(self.entries, height=1, command=self.maximize)
##              else:
##                  b=Button(self.entries, command=self.minimize)
##                 b.grid(column=col, columnspan=2, row=row + 1)
