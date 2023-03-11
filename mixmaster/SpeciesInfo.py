# This file is part of Cantera. See License.txt in the top-level directory or
# at http://www.cantera.org/license.txt for license and copyright information.

import math
import sys
import re

import cantera as ct
from Units import temperature, specificEnergy, specificEntropy
import UnitChooser 
from GraphFrame import Graph

if sys.version_info[0] == 3:
    import tkinter as tk
else:
    import Tkinter as tk


def testit():
    pass


class SpeciesInfo(tk.Label):
    def __init__(self, master, phase=None, species=None, **opt):
        tk.Label.__init__(self, master, opt)
        self.specie = species
        self.phase = phase
        self.bind('<Double-1>', self.show)
        self.bind('<Button-3>', self.show)
        self.bind('<Any-Enter>', self.highlight)
        self.bind('<Any-Leave>', self.nohighlight)

    def highlight(self, event=None):
        self.config(fg='yellow')

    def nohighlight(self, event=None):             
        self.config(fg='darkblue')

    def show(self, event):
        self.new = tk.Toplevel()
        self.new.title(self.specie.symbol)
        #self.new.transient(self.master)
        self.new.bind("<Return>", self.update, "+")
        self.cpr = 0.0
        self.t = 0.0
        self.cpl = 0.0
        self.tl = 0.0
        self.cpp = [[(0.0, 0.0, 'red')]]

        # elemental composition
        self.eframe = tk.Frame(self.new)
        self.eframe.config(relief=tk.GROOVE, bd=4)
        self.eframe.grid(row=0, column=0, columnspan=10, sticky=tk.E + tk.W)
        r = 1
        tk.Label(self.eframe, text='Atoms:').grid(row=0, column=0, sticky=tk.N + tk.W + tk.E)
        for el, c in self.specie.composition:
            tk.Label(self.eframe, text=repr(int(c)) + ' ' + el).grid(row=0, column=r)
            r += 1

        # thermodynamic properties
        self.thermo = tk.Frame(self.new)
        self.thermo.config(relief=tk.GROOVE, bd=4)
        self.thermo.grid(row=1, column=0, columnspan=10, sticky=tk.N + tk.E + tk.W)
        
        label_text = 'Standard Heat of Formation at 298 K: '
        tk.Label(self.thermo, text=label_text).grid(row=0, column=0, sticky=tk.W)
        
        label_text = '%8.2f  kJ / mol' % (self.specie.hf0 * 1.0e-6)
        tk.Label(self.thermo, text=label_text).grid(row=0, column=1, sticky=tk.W)

        tk.Label(self.thermo, text='Molar Mass: ').grid(row=1, column=0, sticky=tk.W)
        label_text = '%8.2f  kg / kmol' % (self.specie.molecularWeight)
        tk.Label(self.thermo, text=label_text).grid(row=1, column=1, sticky=tk.W)

        labels = ['Temperature', 'Specific Heat(c_p)', 'Enthalpy', 'Entropy']
        units = [temperature, specificEntropy, specificEnergy, specificEntropy]
        which_one = [0, 1, 1, 1]

        r = 2
        self.prop = []
        for property in labels:
            tk.Label(self.thermo, text=property).grid(row=r, column=0, sticky=tk.W)
            p = UnitChooser.UnitVar(self.thermo, units[r - 2], which_one[r - 2])
            p.grid(row=r, column=1, sticky=tk.W)
            p.state_variable_entry.config(state=tk.DISABLED, bg='lightgray')
            self.prop.append(p)
            r += 1

        tmin = self.specie.minTemp
        tmax = self.specie.maxTemp
        cp = self.specie.cp_R(tmin)
        enthalpy = self.specie.enthalpy_RT(tmin)
        entropy = self.specie.entropy_R(tmin)

        self.prop[0].bind("<Any-Enter>", self.decouple)
        self.prop[0].bind("<Any-Leave>", self.update)
        self.prop[0].bind("<Key>", self.update)
        self.prop[0].state_variable_entry.config(state=tk.NORMAL, bg='white')
        self.prop[0].set(300.0)

        self.graphs = tk.Frame(self.new)
        self.graphs.config(relief=tk.GROOVE, bd=4)
        self.graphs.grid(row=2, column=0, columnspan=10, sticky=tk.E + tk.W)

        self.cp_data = []
        self.enthalpy_data = []
        self.entropy_data = []
        T_start = tmin
        delta_T = int((tmax - tmin)/100.0)
        while T_start <= tmax:
            self.cp_data.append((T_start, self.specie.cp_R(T_start)))
            self.enthalpy_data.append((T_start, self.specie.enthalpy_RT(T_start)))
            self.entropy_data.append((T_start, self.specie.entropy_R(T_start)))
            T_start += delta_T

        # specific heat plot
        tk.Label(self.graphs, text='c_p/R').grid(row=0, column=0, sticky=tk.W + tk.E)
        ymin, ymax, dtick = self.plotLimits(self.cp_data)
        self.cpg = Graph(self.graphs, '', tmin, tmax, ymin, ymax, pixelX=150, pixelY=150)
        self.cpg.canvas.config(bg='white')
        self.cpg.grid(row=1, column=0, columnspan=2, sticky=tk.W + tk.E)
        self.ticks(ymin, ymax, dtick, tmin, tmax, self.cpg)

        # enthalpy plot
        tk.Label(self.graphs, text='enthalpy/RT').grid(row=0, column=3, sticky=tk.W + tk.E)
        ymin, ymax, dtick = self.plotLimits(self.enthalpy_data)
        self.hg = Graph(self.graphs, '', tmin, tmax, ymin, ymax, pixelX=150, pixelY=150)
        self.hg.canvas.config(bg='white')
        self.hg.grid(row=1, column=3, columnspan=2, sticky=tk.W + tk.E)
        self.ticks(ymin, ymax, dtick, tmin, tmax, self.hg)

        # entropy plot
        tk.Label(self.graphs, text='entropy/R').grid(row=0, column=5, sticky=tk.W + tk.E)
        ymin, ymax, dtick = self.plotLimits(self.entropy_data)
        self.sg = Graph(self.graphs, '', tmin, tmax, ymin, ymax, pixelX=150, pixelY=150)
        self.sg.canvas.config(bg='white')
        self.sg.grid(row=1, column=5, columnspan=2, sticky=tk.W + tk.E)
        self.ticks(ymin, ymax, dtick, tmin, tmax, self.sg)


        self.cpp = []
        for t, cp in self.cp_data:
            self.cpg.join([(t, cp, 'red')])
        for t, h in self.enthalpy_data:
            self.hg.join([(t, h, 'green')])
        for t, s in self.entropy_data:
            self.sg.join([(t, s, 'blue')])

        self.cpdot = self.cpg.plot(tmin, cp, 'red')
        self.hdot = self.hg.plot(tmin, enthalpy, 'green')
        self.sdot = self.sg.plot(tmin, entropy, 'blue')

        b = tk.Button(self.new, text=' OK ', command=self.finished, default=tk.ACTIVE)
        #ed=Button(self.new,text='Edit',command=testit)
        b.grid(column=0, row=4, sticky=tk.W)
        #ed.grid(column=1,row=4,sticky=tk.W)

        self.scfr = tk.Frame(self.new)
        self.scfr.config(relief=tk.GROOVE, bd=4)
        self.scfr.grid(row=3, column=0, columnspan=10, sticky=tk.N + tk.E + tk.W)
        self.sc = tk.Scale(self.scfr, command=self.update, variable=self.prop[0].state_variable_value,
                           orient='horizontal', digits=7, length=400)
        self.sc.config(cnf={'from': tmin, 'to': tmax})
        self.sc.bind('<Any-Enter>', self.couple)
        self.scfr.bind('<Any-Leave>', self.decouple)
        self.sc.grid(row=0, column=0, columnspan=10)

    def decouple(self, event=None):
        d = tk.DoubleVar()
        xx = self.prop[0].get()
        d.set(xx)
        self.sc.config(variable=d)

    def couple(self, event=None):
        self.sc.config(variable=self.prop[0].state_variable_value)
        self.update()

    def update(self, event=None):
        try:
            tmp = self.prop[0].get()
            cnd = self.specie.cp_R(tmp)
            cc = cnd * ct.gas_constant
            self.prop[1].set(cc)
            hnd = self.specie.enthalpy_RT(tmp)
            hh = hnd * tmp * ct.gas_constant
            self.prop[2].set(hh)
            snd = self.specie.entropy_R(tmp)
            ss = snd * tmp * ct.gas_constant
            self.prop[3].set(ss)

            self.cppoint = tmp, cnd
            self.hpoint = tmp, hnd
            self.spoint = tmp, snd
            if hasattr(self, 'cpdot'):
                self.cpg.delete(self.cpdot)
                self.cpdot = self.cpg.plot(self.cppoint[0], self.cppoint[1], 'red')
                self.hg.delete(self.hdot)
                self.hdot = self.hg.plot(self.hpoint[0], self.hpoint[1], 'green')
                self.sg.delete(self.sdot)
                self.sdot = self.sg.plot(self.spoint[0], self.spoint[1], 'blue')
        except:
            pass

    def plotLimits(self, xy):
        ymax = -1.e10
        ymin = 1.e10
        for x, y in xy:
            if y > ymax:
                ymax = y
            if y < ymin:
                ymin = y

        dy = abs(ymax - ymin)
        if dy < 0.2 * ymin:
            ymin = ymin * 0.9
            ymax = ymax * 1.1
            dy = abs(ymax - ymin)
        else:
            ymin -= 0.1 * dy
            ymax += 0.1 * dy
            dy = abs(ymax - ymin)

        p10 = math.floor(math.log10(0.1 * dy))
        fctr = math.pow(10.0, p10)
        mm = [2.0, 2.5, 2.0]
        i = 0
        while dy / fctr > 5:
            fctr = mm[i % 3] * fctr
            i += 1
        ymin = fctr * math.floor(ymin / fctr)
        ymax = fctr * (math.floor(ymax / fctr + 1))
        return ymin, ymax, fctr

    def ticks(self, ymin, ymax, dtick, tmin, tmax, plot):
        ytick = ymin
        eps = 1.e-3
        while ytick <= ymax:
            if abs(ytick) < eps:
                plot.join([(tmin, ytick, 'gray')])
                plot.join([(tmax, ytick, 'gray')])
                plot.last_points = []
            else:
                plot.join([(tmin, ytick, 'gray')])
                plot.join([(tmin + 0.05 * (tmax - tmin), ytick, 'gray')])
                plot.last_points = []
                plot.join([(2.0 * tmax, ytick, 'gray')])
                plot.join([(tmax - 0.05 * (tmax - tmin), ytick, 'gray')])
                plot.last_points = []
            ytick += dtick

    def finished(self, event=None):
        self.new.destroy()
