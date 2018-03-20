# This file is part of Cantera. See License.txt in the top-level directory or
# at http://www.cantera.org/license.txt for license and copyright information.

from __future__ import print_function

import sys

import cantera as ct
from .ElementFrame import getElements
from .utilities import handleError
from .config import *
from .SpeciesFrame import getSpecies

if sys.version_info[0] == 3:
    import tkinter as tk
else:
    import Tkinter as tk


def testit():
    pass


class EditFrame(tk.Frame):
    def __init__(self, master, app):
        tk.Frame.__init__(self, master)
        self.mix = app.mix
        print(self.mix, dir(self.mix))
        self.app = app
        self.master = master
        self.master.title('Cantera Mechanism Editor')
        self.redraw()

    def redraw(self):
        try:
            self.eframe.destroy()
            self.sframe.destroy()
            self.rframe.destroy()
        except:
            pass
        self.addElementFrame()
        self.addSpeciesFrame()
        self.addReactionFrame()

    def addReactionFrame(self):
        self.rframe = tk.Frame(self)
        self.rframe.config(relief=tk.GROOVE, bd=4)
        self.rframe.grid(row=2, column=0, columnspan=10, sticky=tk.E + tk.W)
        b = tk.Button(self.rframe, text='Reactions', command=testit)
        b.grid(column=5, row=0)

    def addElementFrame(self):
        self.eframe = tk.Frame(self)
        self.eframe.config(relief=tk.GROOVE, bd=4)
        self.eframe.grid(row=0, column=0, columnspan=10, sticky=tk.E + tk.W)
        self.element_labels = []
        n = 0
        for el in self.mix._mech.elementNames():
            x = tk.Label(self.eframe, text=el, fg='darkblue')
            x.grid(column=n, row=0)
            self.element_labels.append(x)
            n += 1
        b = tk.Button(self.eframe, text='Element', command=self.chooseElements, default=tk.ACTIVE)
        b.grid(column=0, row=1, columnspan=10)

    def addSpeciesFrame(self):
        self.sframe = tk.Frame(self)
        self.sframe.config(relief=tk.GROOVE, bd=4)
        self.sframe.grid(row=1, column=0, columnspan=10, sticky=tk.E + tk.W)
        r = 0
        c = 0
        splist = self.app.species
        self.spcheck = []
        self.spec = []
        for i in range(self.app.mech.nSpecies()):
            self.spec.append(tk.IntVar())
            self.spec[i].set(1)
            self.spcheck.append(tk.Checkbutton(self.sframe,
                                               text=splist[i].name,
                                               variable=self.spec[i],
                                               onvalue=1, offvalue=0))
            self.spcheck[i].grid(row=r, column=c, sticky=tk.N + tk.W)
            self.spcheck[i].bind("<Button-3>", self.editSpecies)
            c += 1
            if c > 4:
                c, r = 0, r + 1

    def getspecies(self):
        print(getSpecies(self.mix.speciesNames(),
                         self.mix.speciesNames()))

    def editSpecies(self, event=None):
        e = tk.Toplevel(event.widget.master)
        w = event.widget
        txt = w.cget('text')
        sp = self.app.mix.species[txt]

        # name, etc.
        e1 = tk.Frame(e, relief=tk.FLAT)
        self.addEntry(e1, 'Name', 0, 0, sp.name)
        self.addEntry(e1, 'ID Tag', 1, 0, sp.id)
        self.addEntry(e1, 'Phase', 2, 0, sp.phase)
        e1.grid(row=0, column=0)

        # elements
        elframe = tk.Frame(e)
        elframe.grid(row=1, column=0)
        tk.Label(elframe, text='Elemental Composition').grid(row=0, column=0,
                                                             columnspan=2,
                                                             sticky=tk.E + tk.W)

        i = 0
        for el in self.app.mech.elementNames():
            self.addEntry(elframe, el, i, 0, self.mech.nAtoms(sp, el))
            i += 1

        # thermo
        thframe = tk.Frame(e)
        thframe.grid(row=0, rowspan=2, column=1)
        thframe.config(relief=tk.GROOVE, bd=4)
        i = 0
        tk.Label(thframe, text='Thermodynamic Properties').grid(row=0, column=0,
                                                                columnspan=4,
                                                                sticky=tk.E + tk.W)
        if isinstance(sp.thermoParam(), ct.NasaPolynomial):
            tk.Label(thframe, text='Parametrization:').grid(row=1, column=1)
            self.addEntry(thframe, '', 2, 0, 'NasaPolynomial')
            tk.Label(thframe, text='Temperatures (min, mid, max):').grid(row=3, column=1)
            self.addEntry(thframe, '', 4, 0, str(sp.minTemp))
            self.addEntry(thframe, '', 5, 0, str(sp.midTemp))
            self.addEntry(thframe, '', 6, 0, str(sp.maxTemp))
        low = tk.Frame(thframe)
        low.config(relief=tk.GROOVE, bd=4)
        low.grid(row=1, rowspan=6, column=3, columnspan=2)
        tk.Label(low, text='Coefficients for the Low\n Temperature Range').grid(row=0, column=0,
                                                                                columnspan=2,
                                                                                sticky=tk.E + tk.W)
        c = sp.thermoParam().coefficients(sp.minTemp)
        for j in range(7):
            self.addEntry(low, 'a' + str(j), j + 3, 0, str(c[j]))
        high = tk.Frame(thframe)
        high.config(relief=tk.GROOVE, bd=4)
        high.grid(row=1, rowspan=6, column=5, columnspan=2)
        tk.Label(high, text='Coefficients for the High\n Temperature Range').grid(row=0, column=0,
                                                                                  columnspan=2,
                                                                                  sticky=tk.E + tk.W)
        c = sp.thermoParam().coefficients(sp.maxTemp)
        for j in range(7):
            self.addEntry(high, 'a' + str(j), j + 3, 0, str(c[j]))

        com = tk.Frame(e)
        com.grid(row=10, column=0, columnspan=5)
        ok = tk.Button(com, text='OK', default=tk.ACTIVE)
        ok.grid(row=0, column=0)
        ok.bind('<1>', self.modifySpecies)
        tk.Button(com, text='Cancel', command=e.destroy).grid(row=0, column=1)
        self.especies = e

    def modifySpecies(self, event=None):
        button = event.widget
        e = self.especies
        for fr in e.children.values():
            for item in fr.children.values():
                try:
                    print(item.cget('selection'))
                except:
                    pass
        e.destroy()

    def addEntry(self, master, name, row, column, text):
        if name:
            tk.Label(master, text=name).grid(row=row, column=column)
        nm = tk.Entry(master)
        nm.grid(row=row, column=column + 1)
        nm.insert(tk.END, text)

    def chooseElements(self):
        oldel = self.mix.g.elementNames()
        newel = getElements(self.mix.g.elementNames())
        removeList = []
        for el in oldel:
            if not el in newel:
                removeList.append(el)
        #self.app.mech.removeElements(removeList)
        addList = []
        for el in newel:
            if not el in oldel:
                addList.append(el)
        #self.app.mech.addElements(addList)
        try:
            self.redraw()
            self.app.makeWindows()
        except Exception as e:
            handleError('Edit err:\n' + str(e))

        self.app.mix = ct.IdealGasMixture(self.app.mech)
        self.mix = self.app.mix
        nn = self.mix.speciesList[0].name
        self.mix.set(temperature=300.0, pressure=101325.0, moles={nn: 1.0})
        for label in self.element_labels:
            label.destroy()
        self.element_labels = []
        n = 0
        for el in self.mix._mech.elementList():
            x = tk.Label(self.eframe, text=el.symbol(), fg='darkblue')
            x.grid(column=n, row=0)
            self.element_labels.append(x)
            n += 1

        self.app.makeWindows()
