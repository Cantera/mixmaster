# This file is part of Cantera. See License.txt in the top-level directory or
# at http://www.cantera.org/license.txt for license and copyright information.

import numpy as np
import cantera as ct
from utilities import handleError


def species_dict(phase, x):
    """
    Generates a species dictionary with values for the species fractions
    provided by the input. Assumes that input is ordered in the same way as the species
    name list.
    """
    species_names = phase.speciesNames()
    data = {}
    for i, name in enumerate(species_names):
        data[name] = x[i]
    return data


class Species:
    def __init__(self, solution, name):
        self.solution = solution
        t = solution.T
        p = solution.P
        x = solution.X
        self.name = name
        self.symbol = name
        self.index = solution.species_index(name)
        self.minTemp = solution.min_temp
        self.maxTemp = solution.max_temp
        self.molecularWeight = solution.molecular_weights[self.index]
        self.composition = []
        self.element_names = solution.element_names
        self.hf0 = self.enthalpy_RT(298.15) * ct.gas_constant * 298.15
        solution.TPX = t, p, x
        for n in range(len(self.element_names)):
            num_atoms = solution.n_atoms(self.index, n)
            if num_atoms > 0:
                self.composition.append((self.element_names[n], num_atoms))

    def composition(self):
        return self.composition

    def enthalpy_RT(self, t):
        self.solution.TP = t, None
        return self.solution.partial_molar_enthalpies[self.index] / (ct.gas_constant * t)

    def cp_R(self, t):
        self.solution.TP = t, None
        return self.solution.standard_cp_R[self.index]

    def entropy_R(self, t):
        self.solution.TP = t, None
        return self.solution.standard_entropies_R[self.index]


class Mix:
    def __init__(self, solution):
        self.solution = solution
        self._mech = solution
        self.nsp = solution.n_species
        self._moles = np.zeros(self.nsp, 'd')
        self.wt = solution.molecular_weights

    def setMoles(self, m):
        self._moles = m
        self.solution.X = self._moles

    def moles(self):
        return self._moles

    def totalMoles(self):
        sum = 0.0
        for k in range(self.nsp):
            sum += self._moles[k]
        return sum

    def totalMass(self):
        sum = 0.0
        for k in range(self.nsp):
            sum += self._moles[k] * self.wt[k]
        return sum

    def moleDict(self):
        d = {}
        nm = self.solution.species_names
        for e in range(self.nsp):
            d[nm[e]] = self._moles[e]
        return d

    def setMass(self, m):
        self.setMoles(m / self.wt)

    def mass(self):
        return self.wt * self._moles

    def speciesNames(self):
        return self.solution.species_names

    def massDict(self):
        d = {}
        nm = self.solution.species_names
        for e in range(self.nsp):
            d[nm[e]] = self._moles[e] * self.wt[e]
        return d

    def set(self, temperature=None, pressure=None, density=None, enthalpy=None,
            entropy=None, intEnergy=None, equil=0):
        total_mass = self.totalMass()

        if temperature and pressure:
            self.solution.TP = temperature, pressure
            if equil:
                self.solution.equilibrate('TP')

        elif temperature and density:
            self.solution.TD = temperature, density
            if equil:
                self.solution.equilibrate('TV')

        elif pressure and enthalpy:
            self.solution.HP = enthalpy, pressure
            if equil:
                self.solution.equilibrate('HP')

        elif pressure and entropy:
            self.solution.SP = entropy, pressure
            if equil:
                self.solution.equilibrate('SP')

        elif density and entropy:
            self.solution.SV = entropy, 1.0 / density
            if equil:
                self.solution.equilibrate('SV')

        elif density and intEnergy:
            self.solution.UV = intEnergy, 1.0 / density
            if equil:
                self.solution.equilibrate('UV')

#       else:
#               handleError('unsupported property pair', warning=1)

        total_moles = total_mass / self.solution.mean_molecular_weight
        self._moles = self.solution.X * total_moles
