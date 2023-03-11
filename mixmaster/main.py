#############################################################################
#
#  MixMaster
#
#############################################################################

# This file is part of Cantera. See License.txt in the top-level directory or
# at http://www.cantera.org/license.txt for license and copyright information.

import numpy as np
import os
import sys

# Cantera imports
import cantera as ct

# local imports
import utilities
from TransportFrame import TransportFrame
from CompositionFrame import MixtureFrame
from ThermoFrame import ThermoFrame
from ImportFrame import ImportFrame
from DataFrame import DataFrame
from KineticsFrame import SpeciesKineticsFrame, ReactionKineticsFrame, ReactionPathFrame
#from Edit import EditFrame
from MechManager import MechManager, _autoload
from UnitChooser import UnitVar
from ControlPanel import ControlWindow
from ControlPanel import make_menu, menuitem_state
from Mix import Mix, Species

# functionality imports
if sys.version_info[0] == 3:
    import tkinter as tk
    from tkinter import messagebox
    from tkinter.filedialog import askopenfilename
else:
    import Tkinter as tk
    import tkMessageBox as messagebox
    from tkFileDialog import askopenfilename


# options
_app_title = 'MixMaster'
_app_version = '1.1'


class MixMaster:
    """
    This is the primary class that manages the operation of the Mixmaster program.
    """
    def __init__(self, master=None):
        """
        Create a new Application instance.
        Usually this is only called once.
        """
        if master:
            self.master = master
        else:
            self.master = tk.Tk()

        self._windows = {}
        self._vis = {}
        self.windows = []

        self.control_window = ControlWindow(_app_title, self.master)
        self.control_window.master.resizable(tk.FALSE, tk.FALSE)

        self.menu_bar = tk.Frame(self.control_window, relief=tk.GROOVE, bd=2)
        self.menu_bar.grid(row=0, column=0, sticky=tk.N + tk.W + tk.E)

        self.mixture_frame = None
        self.thermo_frame = None
        self.transport_frame = None
        self.kinetics_frame = None
        self.rxndata = None
        self.rxnpaths = None
        self.edit = None
        self.fname = None

        self.mechanism_frame = MechManager(self.control_window, self)
        self.mechanism_frame.grid(row=1, column=0, sticky=tk.N + tk.W)

        file_items = [('Load Mixture...', self.open_mechanism),
                     ('Import Mechanism File...', self.import_file),
                     'separator',
                     ('Load Data File...', self.show_data),
                     'separator',
                     ('Exit', self.stop),
                     []
                     ]
        self.filemenu = make_menu('File', self.menu_bar, file_items)

        self.vtherm = tk.IntVar()  #vtherm = view_thermodynamics?
        self.vcomp = tk.IntVar()
        self.vtran = tk.IntVar()
        self.vkin = tk.IntVar()
        self.vrxn = tk.IntVar()
        self.vrxn.set(0)
        self.vtherm.set(1)
        self.vedit = tk.IntVar()

        #dataitems = [(' Import Flame Data', testit),
        #             (' Import CSV Data', testit),
        #             []]
        # self.datamenu = make_menu('Data', self.menubar, dataitems)

        # toolitems = [(' Convert...', self.importfile),
        #             []]
        # self.toolmenu = make_menu('Tools', self.menubar, toolitems)

        view_items = [(' Thermodynamic State', self.show_thermo, 'check', self.vtherm),
             (' Composition', self.show_composition, 'check', self.vcomp),
          #   (' Transport', self.show_transport, 'check', self.vtran),
             'separator',
             (' Kinetics', self.show_kinetics, 'check', self.vkin),
             (' Reactions...', self.show_reactions),
             (' Reaction Paths...', self.show_reaction_paths),
             []]

        self.view_menu = make_menu('View', self.menu_bar, view_items)

        self.help_menu = make_menu('Help', self.menu_bar,
                                  [('About ' + _app_title + '...', self.about_mix),
                                   ('About Cantera...', self.about_cantera),
                                   []
                                   ])

        # load the preloaded mechanisms
        for mechanism in _autoload:
            self.load_mechanism(mechanism[0], mechanism[1], False)

        self.make_windows()
        self.add_window('import', ImportFrame(self))

        self.vtherm.set(1)
        self.show_thermo()
        ##self.vcomp.set(1)
        ##self.showcomp()

        self.master.iconify()
        self.master.update()
        self.master.deiconify()
        self.control_window.mainloop()

    def stop(self):
        sys.exit(0)

    def open_mechanism(self):
        pathname = askopenfilename(filetypes=[("Cantera Input Files", "*.yaml"),
                                              ("Legacy Cantera Input Files", "*.cti"),
                                              ("XML Files", "*.xml *.ctml"),
                                              ("All Files", "*.*")])
        if pathname:
            self.load_mechanism('', pathname)

    def load_mechanism(self, mechanism_name, pathname, make_window=True):
        p = os.path.normpath(os.path.dirname(pathname))
        self.fname = os.path.basename(pathname)
        ff = os.path.splitext(self.fname)

        try:
            self.mech = ct.Solution(pathname)
            self.mechname = ff[0]

        except Exception as e:
            utilities.handleError('could not create gas mixture object: '
                                  + ff[0] + '\n' + str(e))
            self.mechname = 'Error'
            return

        self.make_mixture()

        if not mechanism_name:
            mechanism_name = self.mechname

        self.mechanism_frame.addMechanism(mechanism_name, self.mech)
        if make_window == True:
            self.make_windows()

    def add_window(self, name, window):
        """Add a new window, or replace an existing one."""
        window_state = ''
        if name in self._windows:
            try:
                window_state = self._windows[name].master.state()
                self._windows[name].master.destroy()
            except:
                pass
        else:
            window_state = 'withdrawn'
        self._windows[name] = window
        self._vis[name] = tk.IntVar()
        if window_state == 'withdrawn':
            self._windows[name].master.withdraw()
        else:
            self._windows[name].show()

    def update(self):
        """Update all windows to reflect the current mixture state."""
        for window in self._windows.keys():
            try:
                m = self._windows[window].master
                if m.state() != 'withdrawn':
                    self._windows[window].show()
            except:
                pass
        self.thermo_frame.showState()
        self.mixture_frame.show()

    def make_mixture(self):
        self.mix = Mix(self.mech)
        species_names = self.mech.species_names
        self.species = [Species(self.mech, name) for name in species_names]
    
        x = self.mech.X
        self.mix.setMoles(x)
        self.mix.set(temperature=self.mech.T, pressure=self.mech.P)

    def import_file(self):
        #self.vimport.set(1)
        window = self._windows['import']
        window.show()

    def make_windows(self):
#        if self.mixture_frame:
        for window in self.windows:
            try:
                window.destroy()
            except:
                pass

        self.mixture_frame = MixtureFrame(self.control_window, self)
        self.thermo_frame = ThermoFrame(self.control_window, self)
        self.transport_frame = TransportFrame(self.control_window, self)

        self.kinetics_frame = SpeciesKineticsFrame(self.control_window, self)

        self.add_window('rxndata', ReactionKineticsFrame(self.vrxn, self))
        self.add_window('rxnpaths', ReactionPathFrame(self))
        self.add_window('dataset', DataFrame(None, self))

        #self.edit = EditFrame(t, self)

        self.windows = [self.mixture_frame, self.thermo_frame, self.transport_frame, self.kinetics_frame]

        self.show_thermo()
        self.show_composition()
        self.show_transport()
        self.show_kinetics()
        #self.showrxns()
        #self.showrpaths()
        #self.showdata()

        if self.mech:
            self.mechanism_frame.grid(row=1, column=0)
        else:
            self.mechanism_frame.grid_forget()
        #self.showedit()

    def show(self, frame, vis, row, col):
        if vis:
            frame.grid(row=row, column=col, sticky=tk.N + tk.E + tk.S + tk.W)
        else:
            frame.grid_forget()

    def show_thermo(self):
        if self.thermo_frame:
            self.show(self.thermo_frame, self.vtherm.get(), 7, 0)

    def show_composition(self):
        if self.mixture_frame:
            self.show(self.mixture_frame, self.vcomp.get(), 8, 0)
    
    def show_transport(self):
        if self.transport_frame:
            self.show(self.transport_frame, self.vtran.get(), 9, 0)    

    def show_kinetics(self):
        if self.kinetics_frame:
            self.show(self.kinetics_frame, self.vkin.get(), 10, 0)

    def show_reactions(self):
        self._windows['rxndata'].show()

    def show_reaction_paths(self):
        self._windows['rxnpaths'].show()

    def show_data(self):
        self._windows['dataset'].browseForDatafile()

    def about_mix(self):
        message_string = """
        MixMaster

        version """ + _app_version + """

        written by:

        Prof. David G. Goodwin
        California Institute of Technology

        copyright 2003
        California Institute of Technology
        """
        m = messagebox.showinfo(title='About MixMaster', message=message_string)

    def about_cantera(self):
        message_string = """
        Cantera
        
        version""" + ct.__version__ + """
        
        http://cantera.github.io/docs/sphinx/html/index.html
        
        """
        m = messagebox.showinfo(title='About Cantera', message=message_string)


if __name__ == "__main__":
    MixMaster()
