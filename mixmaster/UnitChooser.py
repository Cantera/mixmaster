# This file is part of Cantera. See License.txt in the top-level directory or
# at http://www.cantera.org/license.txt for license and copyright information.

import re
import sys

if sys.version_info[0] == 3:
    import tkinter as tk
else:
    import Tkinter as tk


class UnitVar(tk.Frame):
    """
    A frame to display the units that a user can select. This class makes use of the Units modules.

    TODO: See if this implementation can leverage the more modern handling of units in the main Cantera repo.
    """
    def __init__(self, master, unit_module, default_unit=0):
        """
        unit_module: a module that is particular to a type of unit. Like temperature or density.
        """
        tk.Frame.__init__(self, master)
        self.state_variable_value = tk.DoubleVar()
        self.state_variable_value.set(0.0)
        self.state_variable_value_SI = 0.0
        self.unit_module = unit_module
        try:
            self.unit_list = self.unit_module.units
        except:
            self.unit_list = []
            unit_list=dir(self.unit_module)
            for entry in unit_list:
                if entry[0] != '_':
                    self.unit_list.append(entry)

        self.state_variable_entry = tk.Entry(self, textvariable=self.state_variable_value)

        self.unit_display_name = tk.StringVar()
        unit_name = re.sub('__', ' / ', self.unit_list[default_unit])
        self.unit_display_name.set(unit_name)

        self.conversion_factor = eval('self.unit_module.' + re.sub(' / ', '__', self.unit_display_name.get())).value
        self.unit_display_label = tk.Label(self)
        self.unit_display_label.config(textvariable=self.unit_display_name, fg='darkblue')
        self.unit_display_label.bind('<Double-1>', self.select)
        self.unit_display_label.bind('<Any-Enter>', self.highlight)
        self.unit_display_label.bind('<Any-Leave>', self.nohighlight)
        self.state_variable_entry.grid(row=0, column=0)
        self.unit_display_label.grid(row=0, column=1)

    def highlight(self, event=None):
        self.unit_display_label.config(fg='yellow')

    def nohighlight(self, event=None):
        self.unit_display_label.config(fg='darkblue')

    def select(self, event):
        """
        Opens up a new window to select a new unit basis for the variable.
        """
        self.new = tk.Toplevel()
        self.new.title("Units")
        self.new.transient(self.master)
        self.new.bind("<Return>", self.finished, "+")

        unit_row_location = 0
        unit_column_location = 0
        max_units_per_column = 10
        for unit in self.unit_list:
            if unit[0] != '_' and unit[:1] != '__' and unit != 'SI':
                unit = re.sub('__', ' / ', unit)
                tk.Radiobutton(self.new, text=unit, variable=self.unit_display_label['textvariable'],
                               value=unit, command=self.update,
                               ).grid(column=unit_column_location, row=unit_row_location,sticky=tk.W, padx=20)

                unit_row_location+= 1
                if unit_row_location > max_units_per_column:
                    unit_row_location = 0
                    unit_column_location += 1
                    unit_row_location += 1

        button = tk.Button(self.new, text='OK', command=self.finished, default=tk.ACTIVE)
        button.grid(column=unit_column_location, row=unit_row_location, padx=20)

        self.new.wait_visibility()
        self.new.grab_set()
        self.new.focus_set()
        self.new.wait_window()

    def finished(self, event=None):
        self.new.destroy()

    def update(self):
        """
        Performs the update to the value of the stored unit once a users selects a partcular unit
        to express an input state variable in. Stores the value of the unit in SI, then updates the value
        and also updates the conversion factor from the new unit to the SI unit.
        """
        self.state_variable_value_SI = self.state_variable_value.get() * self.conversion_factor
        self.conversion_factor = eval('self.unit_module.' + re.sub(' / ', '__', self.unit_display_name.get())).value
        self.state_variable_value.set(self.state_variable_value_SI / self.conversion_factor)

    def get(self):
        self.state_variable_value_SI = self.state_variable_value.get() * self.conversion_factor
        return self.state_variable_value_SI

    def set(self, value):
        self.state_variable_value_SI = value
        self.state_variable_value.set(value / self.conversion_factor)
