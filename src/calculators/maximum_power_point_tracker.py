from decimal import Decimal
from functools import lru_cache
from typing import Final

import scipy
from astropy import units as u

from src.calculators.total_power_output import TotalPowerOutput


class MaximumPowerPointTracker:
    cache: dict[
        tuple[u.Quantity, u.Quantity, u.Quantity, u.Quantity], u.Quantity
    ] = dict()

    def __init__(
        self,
        t_sky: u.Quantity,
        t_cell: u.Quantity,
        E_g: u.Quantity,
    ):
        self.t_sky: Final[u.Quantity] = t_sky
        self.t_cell: Final[u.Quantity] = t_cell
        self.E_g: Final[u.Quantity] = E_g

        voltage_optimise_function: Final[
            scipy.optimize.OptimizeResult
        ] = scipy.optimize.minimize_scalar(fun=self._power_output, bounds=[-5.0, 0.0])
        self.optimal_voltage: Final[u.Quantity] = (
            round(voltage_optimise_function.x, 3) * u.volt
        )
        self.max_power: Final[u.Quantity] = -voltage_optimise_function.fun * (
            u.watt / u.meter**2
        )  #  Changed sign for minimize function to get maximize, now undo

    def _power_output(self, voltage: float):
        voltage_decimal: Final[Decimal] = Decimal(voltage).quantize(Decimal(".001"))
        return -self._calculate_power_output_for_voltage(
            voltage=(voltage_decimal * u.volt),
            E_g=self.E_g,
            t_cell=self.t_cell,
            t_sky=self.t_sky,
        )

    @classmethod
    @lru_cache(maxsize=None)
    def _calculate_power_output_for_voltage(
        self,
        voltage: u.Quantity,
        E_g: u.Quantity,
        t_sky: u.Quantity,
        t_cell: u.Quantity,
    ) -> float:
        voltage = round(voltage.value, 3) * u.volt
        t_sky = round(t_sky.value) * u.Kelvin
        t_cell = round(t_cell.value) * u.Kelvin

        cache_lookup: tuple[u.Quantity, u.Quantity, u.Quantity, u.Quantity] = (
            voltage,
            E_g,
            t_sky,
            t_cell,
        )
        if cache_lookup not in self.cache:
            chemical_potential_driving_emission: Final[u.Quantity] = (
                voltage.value * u.eV
            )
            power_output: Final[u.Quantity] = (
                TotalPowerOutput(E_g=E_g)
                .get_total_power_output(
                    voltage=voltage,
                    t_sky=t_sky,
                    t_cell=t_cell,
                    chemical_potential_driving_emission=chemical_potential_driving_emission,
                )
                .value
                * u.watt
            )
            self.cache[cache_lookup] = power_output
            return power_output.value
        else:
            return self.cache[cache_lookup].value
