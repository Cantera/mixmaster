# This file is part of Cantera. See License.txt in the top-level directory or
# at http://www.cantera.org/license.txt for license and copyright information.

import sys
import cantera as ct

if sys.version_info[0] == 3:
    import tkinter as tk
    from tkinter.filedialog import askopenfilename
    from tkinter import messagebox
else:
    import Tkinter as tk
    import tkMessageBox as messagebox
    from tkFileDialog import askopenfilename


class NewFlowDialog:
    def __init__(self, parent):
        top = self.top = tk.Toplevel(parent)

        pl = tk.Label(top, text='Pressure')
        pl.grid(row=0, column=0)

        geom = tk.Frame(top, bd=2, relief=tk.GROOVE)
        geom.grid(row=1, column=0)
        lb = tk.Listbox(geom)
        for item in ['One-Dimensional', 'Stagnation']:
            lb.insert(tk.END, item)
        lb.grid(row=0, column=0)
        glb = tk.Listbox(geom)
        for item in ['Axisymmetric', '2D']:
            glb.insert(tk.END, item)
        glb.grid(row=1, column=0)

        # ------------- pressure input ----------------
        self.p = tk.DoubleVar()
        self.pbox = tk.Entry(top, textvariable=self.p)
        self.pbox.grid(row=0, column=1)

        # ------------- gas file name input -----------
        gasf = tk.Frame(top, bd=2, relief=tk.GROOVE)
        gasf.grid(row=4, column=0, columnspan=2)
        gl = tk.Label(gasf, text='Gas Mixture Specification')
        gl.grid(row=0, column=0)

        self.infile = tk.StringVar()
        tk.Label(gasf, text='Mixture Input File').grid(row=1, column=0)
        tk.Entry(gasf, textvariable=self.infile).grid(row=1, column=1)
        tk.Button(gasf, text='Browse..', command=self.getinfile).grid(row=1, column=2)

        self.spfile = tk.StringVar()
        tk.Label(gasf, text='Species Database').grid(row=2, column=0)
        tk.Entry(gasf, textvariable=self.spfile).grid(row=2, column=1)
        tk.Button(gasf, text='Browse..', command=self.getspfile).grid(row=2, column=2)

        self.trfile = tk.StringVar()
        tk.Label(gasf, text='Transport Database').grid(row=3, column=0)
        tk.Entry(gasf, textvariable=self.trfile).grid(row=3, column=1)
        tk.Button(gasf, text='Browse..', command=self.gettrfile).grid(row=3, column=2)

        # ------------- grid -------------------------
        gf = tk.Frame(top, bd=2, relief=tk.GROOVE)
        gf.grid(row=5, column=0, columnspan=2)

        gr = tk.Label(gf, text='Initial Grid')
        gr.grid(row=0, column=0)

        self.zleft = tk.DoubleVar()
        self.zright = tk.DoubleVar()
        ll = tk.Label(gf, text='Left boundary at ')
        rl = tk.Label(gf, text='Right boundary at ')
        lbb = tk.Entry(gf, textvariable=self.zleft)
        rbb = tk.Entry(gf, textvariable=self.zright)
        ll.grid(row=1, column=0)
        rl.grid(row=2, column=0)
        lbb.grid(row=1, column=1)
        rbb.grid(row=2, column=1)

        ok = tk.Button(top, text='OK', command=self.ok)
        ok.grid(row=20, column=20)

    def ok(self):
        p = self.p.get()
        try:
            infile = self.infile.get()
            spfile = self.spfile.get()
            trfile = self.trfile.get()
            if spfile and trfile:
                self.gas = ct.IdealGasMix(import_file=infile,
                                          thermo_db=spfile,
                                          transport_db=trfile)
            elif spfile:
                self.gas = ct.IdealGasMix(import_file=infile,
                                          thermo_db=spfile)
            else:
                self.gas = ct.IdealGasMix(import_file=infile)

        except:
            messagebox.showerror('Create Gas',
                                 'Error reading file %s. See log file for more information.' % infile)

        #self.flow = Flow1D(flow_type = ftype, flow_geom = fgeom,
        #                   pressure = p, grid = gr, gas = g)
        self.top.destroy()

    def getinfile(self):
        pathname = askopenfilename(filetypes=[
            ("Input Files", "*.xml *.inp"),
            ("All Files", "*.*")])
        self.infile.set(pathname)

    def getspfile(self):
        pathname = askopenfilename(filetypes=[
            ("Species Data Files", "*.xml *.dat"),
            ("All Files", "*.*")])
        self.spfile.set(pathname)

    def gettrfile(self):
        pathname = askopenfilename(filetypes=[
            ("Transport Data Files", "*.xml *.dat"),
            ("All Files", "*.*")])
        self.trfile.set(pathname)
