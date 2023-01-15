import math
from typing import Final

import mpmath
import numpy
import scipy.integrate as integrate

from src.constants import Constants


class TotalPowerOutput:
    def __init__(self, E_g):
        self.E_g: Final[float] = E_g

    def get_photon_flux_emitted_from_semiconductor(
        self, T: float | int, voltage: float
    ) -> float:
        """
        :param T: temperature of the semiconductor
        :param voltage: voltage produced by cell
        :return:
        """
        Delta_mu: Final[float] = Constants.q * voltage

        term_1: Final[float] = (2 * math.pi) / (Constants.h**3 * Constants.c**2)
        term_2: Final[float] = integrate.quad(
            lambda E: self.get_term_in_photon_flux_integration(
                E=E, T=T, Delta_mu=Delta_mu
            ),
            numpy.inf,
            self.E_g,
        )[0]
        return term_1 * term_2

    def get_term_in_photon_flux_integration(
        self, E: float, T: float | int, Delta_mu: float
    ) -> float:
        print(f"Trying E={E}")
        result = (self.get_energy_dependent_emissivity(E) * E**2) / (
            mpmath.exp(E - Delta_mu / (Constants.k_B * T)) - 1
        )
        print(result)
        return result

    def get_energy_dependent_emissivity(self, E: float) -> float | int:
        """
        :param E: photon energy [eV]
        :return: energy-dependent emissivity epsilon(E)
        """
        return 0 if E < self.E_g else 1
