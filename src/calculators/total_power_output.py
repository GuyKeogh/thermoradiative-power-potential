import math
from typing import Final

import mpmath
import numpy as np
import scipy.integrate as integrate
from astropy import constants as const
from astropy import units as u
from astropy.units import Quantity

from src.constants import Constants
from src.exceptions import UnitError


class TotalPowerOutput:
    def __init__(self, E_g):
        self.E_g: Final[Quantity] = E_g
        self.integration_iterator = 0
        self.integration_results_dict: dict[int, tuple[float, float]] = dict()

    def get_photon_flux_emitted_from_semiconductor(
        self, T: Quantity, Delta_mu: Quantity
    ) -> Quantity:
        """
        :param T: temperature of the semiconductor
        :param voltage: voltage produced by cell
        :return:
        """
        term_1: Final[Quantity] = (2 * math.pi) / (
            (const.si.h.to(u.electronvolt / u.hertz)) ** 3 * const.c**2
        )

        E_unit: Final[u.Unit] = u.electronvolt
        term_2: Final[Quantity] = (
            integrate.quad(
                lambda E: self._get_term_in_photon_flux_integration(
                    E=E * E_unit, T=T, Delta_mu=Delta_mu
                ).value,
                self.E_g.to(E_unit).value,
                np.inf,
            )[0]
            * E_unit
        )

        # integration_results_df = pd.DataFrame.from_dict(data=self.integration_results_dict, orient="index", columns=["E", "integration_result"])
        # integration_results_df.to_csv("integration_results.csv")
        return term_1 * term_2

    def _get_term_in_photon_flux_integration(
        self, E: Quantity, T: Quantity, Delta_mu: Quantity
    ) -> Quantity:
        # print(f"Trying E={E}")

        exponential_term_quantity: Final[Quantity] = (E - Delta_mu) / (
            const.k_B.to(u.electronvolt / u.Kelvin) * T
        )
        if exponential_term_quantity.unit != u.dimensionless_unscaled:
            raise UnitError(
                f"Exponential term should be dimensionless, not {exponential_term_quantity.unit}"
            )
        exponential_term: Final[float] = exponential_term_quantity.value

        result = (self.get_energy_dependent_emissivity(E) * E**2) / (
            mpmath.exp(exponential_term) - 1
        )

        # print(f"Exp term: {exponential_term}")
        self.integration_results_dict[self.integration_iterator] = (E.value, result)
        self.integration_iterator += 1
        return result

    def get_energy_dependent_emissivity(self, E: Quantity) -> float | int:
        """
        :param E: photon energy [eV]
        :return: energy-dependent emissivity epsilon(E)
        """

        return 0 if E.to(self.E_g.unit) < self.E_g else 1

    def get_extractible_power_density(self, t_surface: Quantity) -> Quantity:
        V: Final[Quantity] = -0.1 * u.volt
        flux_from_atmosphere: Final[
            Quantity
        ] = self.get_photon_flux_emitted_from_semiconductor(
            T=Constants.T_deep_space, Delta_mu=(0 * u.electronvolt)
        )  # .value * (u.second / (u.meter**2))
        flux_from_cell: Final[
            Quantity
        ] = self.get_photon_flux_emitted_from_semiconductor(
            T=t_surface, Delta_mu=(Constants.q * V).to(u.electronvolt)
        )
        P = Constants.q * V * (flux_from_atmosphere - flux_from_cell)
        # return flux_from_cell
        return P
