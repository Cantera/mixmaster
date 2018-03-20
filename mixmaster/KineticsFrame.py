# This file is part of Cantera. See License.txt in the top-level directory or
# at http://www.cantera.org/license.txt for license and copyright information.

from __future__ import print_function

import math
import os
import sys
import webbrowser

import cantera as ct
from SpeciesInfo import SpeciesInfo

if sys.version_info[0] == 3:
    import tkinter as tk
else:
    import Tkinter as tk


_CUTOFF = 1.e-15
_ATOL = 1.e-15
_RTOL = 1.e-7


def showsvg():
    f = open('_rp_svg.html', 'w')
    f.write('<embed src="rxnpath.svg" name="rxnpath" height=500\n')
    f.write('type="image/svg-xml" pluginspage="http://www.adobe.com/svg/viewer/install/">\n')
    f.close()
    webbrowser.open('file:///' + os.getcwd() + '/_rp_svg.html')


def showpng():
    f = open('_rp_png.html', 'w')
    f.write('<img src="rxnpath.png" height=500/>\n')
    f.close()
    webbrowser.open('file:///' + os.getcwd() + '/_rp_png.html')


class KineticsFrame(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.config(relief=tk.FLAT, bd=4)
        self.top = self.master.top
        self.controls = tk.Frame(self)
        self.hide = tk.IntVar()
        self.hide.set(0)
        self.comp = tk.IntVar()
        self.comp.set(2)
        self.controls.grid(column=1, row=0, sticky=tk.W + tk.E + tk.N)
        self.makeControls()
        mf = self.master

    def makeControls(self):
        tk.Radiobutton(self.controls, text='Creation Rates',
                       variable=self.comp, value=0,
                       command=self.show).grid(column=0, row=0, sticky=tk.W)
        tk.Radiobutton(self.controls, text='Destruction Rates',
                       variable=self.comp, value=1,
                       command=self.show).grid(column=0, row=1, sticky=tk.W)
        tk.Radiobutton(self.controls, text='Net Production Rates',
                       variable=self.comp, value=2,
                       command=self.show).grid(column=0, row=2, sticky=tk.W)

    def show(self):
        mf = self.master
        mf.active = self
        c = self.comp.get()
        mix = self.top.mix
        g = mix.g
        if c == 0:
            mf.var.set('Creation Rates')
            #mf.data = spdict(mix.g, mix.moles())
            mf.comp = g.creation_rates

        elif c == 1:
            mf.var.set('Destruction Rates')
            #mf.data = spdict(mix.g,mix.mass())
            mf.comp = g.destruction_rates

        elif c == 2:
            mf.var.set('Net Production Rates')
            mf.comp = g.net_production_rates
            #mf.data = spdict(mix,mix,mf.comp)

        for s in mf.variable.keys():
            try:
                k = g.species_index(s)
                if mf.comp[k] > _CUTOFF or -mf.comp[k] > _CUTOFF:
                    mf.variable[s].set(mf.comp[k])
                else:
                    mf.variable[s].set(0.0)
            except:
                pass


class SpeciesKineticsFrame(tk.Frame):
    def __init__(self, master, top):
        tk.Frame.__init__(self, master)
        self.config(relief=tk.GROOVE, bd=4)
        self.top = top
        self.top.kinetics = self
        self.g = self.top.mix.g
        self.entries = tk.Frame(self)
        self.var = tk.StringVar()
        self.var.set("Net Production Rates")
        self.names = self.top.mix.speciesNames()
        self.nsp = len(self.names)
        self.comp = [0.0] * self.nsp
        self.makeControls()
        self.makeEntries()
        self.entries.bind('<Double-l>', self.minimize)
        self.ctype = 0

    def makeControls(self):
        self.c = KineticsFrame(self)
        #self.rr = ReactionKineticsFrame(self, self.top)
        self.c.grid(column=1, row=0, sticky=tk.E + tk.W + tk.N + tk.S)
        #self.rr.grid(column=0, row=1, sticky=E+W+N+S)

    def show(self):
        self.c.show()

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

    def makeEntries(self):
        self.entries.grid(row=0, column=0, sticky=tk.W + tk.N + tk.S + tk.E)
        self.entries.config(relief=tk.FLAT, bd=4)
        DATAKEYS = self.top.species
        self.variable = {}

        n = 0
        ncol = 3
        col = 0
        row = 60
        for sp in DATAKEYS:
            s = sp
            k = s.index
            if row > 15:
                row = 0
                col += 2
                l = tk.Label(self.entries, text='Species')
                l.grid(column=col, row=row, sticky=tk.E + tk.W)
                e1 = tk.Entry(self.entries)
                e1.grid(column=col + 1, row=row, sticky=tk.E + tk.W)
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
                entry1.config(state=tk.DISABLED, bg='lightgray')


class ReactionKineticsFrame(tk.Frame):
    def __init__(self, vis, top):
        self.master = tk.Toplevel()
        self.master.protocol("WM_DELETE_WINDOW", self.hide)
        self.vis = vis
        tk.Frame.__init__(self, self.master)
        self.config(relief=tk.GROOVE, bd=4)
        self.top = top
        self.g = self.top.mix.g
        nr = self.g.n_reactions
        self.eqs = tk.Text(self, width=40, height=30)
        self.data = []
        self.start = tk.DoubleVar()
        if nr > 30:
            self.end = self.start.get()+30
        else:
            self.end = self.start.get()+nr

        for i in range(4):
            self.data.append(tk.Text(self, width=15, height=30))

        for n in range(nr):
            s = self.g.reaction_equation(n)
            self.eqs.insert(tk.END, s + '\n')
        self.eqs.grid(column=0, row=1, sticky=tk.W + tk.E + tk.N)
        for i in range(4):
            self.data[i].grid(column=i + 1, row=1, sticky=tk.W + tk.E + tk.N)
        tk.Label(self, text='Reaction').grid(column=0, row=0, sticky=tk.W + tk.E + tk.N)
        tk.Label(self, text='Fwd ROP').grid(column=1, row=0, sticky=tk.W + tk.E + tk.N)
        tk.Label(self, text='Rev ROP').grid(column=2, row=0, sticky=tk.W + tk.E + tk.N)
        tk.Label(self, text='Net ROP').grid(column=3, row=0, sticky=tk.W + tk.E + tk.N)
        tk.Label(self, text='Kp').grid(column=4, row=0, sticky=tk.W + tk.E + tk.N)

        self.scfr = tk.Frame(self)
        self.scfr.config(relief=tk.GROOVE, bd=4)

       #self.sc = Scrollbar(self.scfr,command=self.show,
       #                    variable = self.start,
       #                    orient='horizontal',length=400)
        self.sc = tk.Scale(self.scfr, command=self.show, variable=self.start,
                           orient='vertical', length=400)
        #self.sc.config(cnf={'from':0,'to':nr},variable = self.start)
        #self.sc.bind('<Any-Enter>',self.couple)
        #self.scfr.bind('<Any-Leave>',self.decouple)
        self.sc.pack(side=tk.RIGHT, fill=tk.Y)
        self.scfr.grid(row=0, column=6, rowspan=10, sticky=tk.N + tk.E + tk.W)
        self.grid(column=0, row=0)

        self.hide()

##      def decouple(self,event=None):
##              d = DoubleVar()
##              xx = self.start.get()
##              d.set(xx)
##              self.sc.config(variable = d)

##      def couple(self,event=None):
##              self.sc.config(variable = self.start)

    def hide(self):
        #self.vis.set(0)
        self.master.withdraw()

    def show(self, e=None, b=None, c=None):
        v = self.vis.get()
        print(e, b, c)
        #if v == 0:
        #       self.hide()
        #       return

        self.master.deiconify()
        nr = self.g.n_reactions
        frop = self.g.forward_rates_of_progress
        rrop = self.g.reverse_rates_of_progress
        kp = self.g.equilibrium_constants
        self.data[0].delete(1.0, tk.END)
        self.data[1].delete(1.0, tk.END)
        self.data[2].delete(1.0, tk.END)
        self.data[3].delete(1.0, tk.END)
        self.eqs.delete(1.0, tk.END)

        n0 = int(self.start.get())
        nn = nr - n0
        if nn > 30:
            nn = 30
        for n in range(n0, nn + n0):
            s = '%12.5e \n' % (frop[n],)
            self.data[0].insert(tk.END, s)
            s = '%12.5e \n' % (rrop[n],)
            self.data[1].insert(tk.END, s)
            s = '%12.5e \n' % (frop[n] - rrop[n],)
            self.data[2].insert(tk.END, s)
            s = '%12.5e \n' % (kp[n],)
            self.data[3].insert(tk.END, s)
            self.eqs.insert(tk.END, self.g.reaction_equation(n) + '\n')


class ReactionPathFrame(tk.Frame):
    def __init__(self, top):
        self.master = tk.Toplevel()
        self.master.protocol("WM_DELETE_WINDOW", self.hide)
        # self.vis = vis
        tk.Frame.__init__(self, self.master)
        self.config(relief=tk.GROOVE, bd=4)
        self.grid(column=0, row=0)
        self.top = top
        self.g = self.top.mix.g
        self.el = tk.IntVar()
        self.el.set(0)
        self.thresh = tk.DoubleVar()

        scframe = tk.Frame(self)
        self.sc = tk.Scale(scframe, variable=self.thresh, orient='horizontal',
                           digits=3, length=300, resolution=0.01)
        self.sc.config(cnf={'from': -6, 'to': 0})
        tk.Label(scframe, text='log10 Threshold').grid(column=0, row=0)
        self.sc.grid(row=0, column=1, columnspan=10)
        self.sc.bind('<ButtonRelease-1>', self.show)
        scframe.grid(row=3, column=0, columnspan=10)

        enames = self.g.element_names
        self.nel = len(enames)

        i = 1
        eframe = tk.Frame(self)
        tk.Label(eframe, text='Element').grid(column=0, row=0, sticky=tk.W)
        for e in enames:
            tk.Radiobutton(eframe, text=e, variable=self.el, value=i - 1,
                           command=self.show).grid(column=i, row=0, sticky=tk.W)
            i += 1
        eframe.grid(row=0, column=0)

        self.detailed = tk.IntVar()
        tk.Checkbutton(self, text='Show details', variable=self.detailed,
                       command=self.show).grid(column=1, row=0)
        self.net = tk.IntVar()
        tk.Checkbutton(self, text='Show net flux', variable=self.net,
                       command=self.show).grid(column=2, row=0)
        self.local = tk.StringVar()
        tk.Label(self, text='Species').grid(column=1, row=1, sticky=tk.E)
        sp = tk.Entry(self, textvariable=self.local, width=15)
        sp.grid(column=2, row=1)
        sp.bind('<Any-Leave>', self.show)

        self.fmt = tk.StringVar()
        self.fmt.set('svg')
        i = 1
        fmtframe = tk.Frame(self)
        fmtframe.config(relief=tk.GROOVE, bd=4)
        self.browser = tk.IntVar()
        self.browser.set(0)
        tk.Checkbutton(fmtframe, text='Display in Web Browser',
                       variable=self.browser,
                       command=self.show).grid(column=0, columnspan=6, row=0)
        tk.Label(fmtframe, text='Format').grid(column=0, row=1, sticky=tk.W)

        for e in ['svg', 'png', 'gif', 'jpg']:
            tk.Radiobutton(fmtframe, text=e, variable=self.fmt, value=e,
                           command=self.show).grid(column=i, row=1, sticky=tk.W)
            i += 1
        fmtframe.grid(row=5, column=0, columnspan=10, sticky=tk.E + tk.W)

        self.cv = tk.Canvas(self, relief=tk.SUNKEN, bd=1)
        self.cv.grid(column=0, row=4, sticky=tk.W + tk.E + tk.N, columnspan=10)

        pframe = tk.Frame(self)
        pframe.config(relief=tk.GROOVE, bd=4)
        self.dot = tk.StringVar()
        self.dot.set('dot -Tgif rxnpath.dot > rxnpath.gif')
        tk.Label(pframe, text='DOT command:').grid(column=0, row=0, sticky=tk.W)
        tk.Entry(pframe, width=60, textvariable=self.dot).grid(column=0, row=1, sticky=tk.W)
        pframe.grid(row=6, column=0, columnspan=10, sticky=tk.E + tk.W)

        self.thresh.set(-2.0)
        self.hide()

    def hide(self):
        #self.vis.set(0)
        self.master.withdraw()

    def show(self, e=None):
        self.master.deiconify()
        el = self.g.element_name(self.el.get())
        det = False
        if self.detailed.get() == 1:
            det = True
        flow = 'OneWayFlow'
        if self.net.get() == 1:
            flow = 'NetFlow'

        self.d = ct.ReactionPathDiagram(self.g, el)
        self.d.arrow_width = -2
        self.d.flow_type = flow
        self.d.show_details = det
        self.d.threshold = math.pow(10.0, self.thresh.get())
        node = self.local.get()
        try:
            k = self.g.species_index(node)
            self.d.display_only(k)
        except:
            self.d.display_only(-1)

        self.d.write_dot('rxnpath.dot')

        if self.browser.get() == 1:
            fmt = self.fmt.get()
            os.system('dot -T' + fmt + ' rxnpath.dot > rxnpath.' + fmt)
            if fmt == 'svg':
                showsvg()
            elif fmt == 'png':
                showpng()
            else:
                path = 'file:///' + os.getcwd() + '/rxnpath.' + fmt
                webbrowser.open(path)
            try:
                self.cv.delete(self.image)
            except:
                pass
            self.cv.configure(width=0, height=0)
        else:
            os.system(self.dot.get())
            self.rp = None
            try:
                self.cv.delete(self.image)
            except:
                pass
            try:
                self.rp = tk.PhotoImage(file='rxnpath.gif')
                self.cv.configure(width=self.rp.width(), height=self.rp.height())
                self.image = self.cv.create_image(0, 0, anchor=tk.NW, image=self.rp)
            except:
                pass
