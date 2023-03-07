from typing import Final

import scipy
from astropy import units as u

from src.calculators.total_power_output import TotalPowerOutput


class MaximumPowerPointTracker:
    cache: dict[
        tuple[u.Quantity, u.Quantity, u.Quantity], tuple[u.Quantity, u.Quantity]
    ] = dict()

    def __init__(
        self,
        t_sky: u.Quantity,
        t_cell: u.Quantity,
        E_g: u.Quantity,
    ):
        t_sky = round(t_sky.value, 1) * t_sky.unit
        t_cell = round(t_cell.value, 1) * t_cell.unit
        self.t_sky: Final[u.Quantity] = t_sky
        self.t_cell: Final[u.Quantity] = t_cell
        self.E_g: Final[u.Quantity] = E_g

        cache_lookup: tuple[u.Quantity, u.Quantity, u.Quantity] = (
            E_g,
            t_sky,
            t_cell,
        )

        if cache_lookup not in self.cache:
            voltage_optimise_function: Final[
                scipy.optimize.OptimizeResult
            ] = scipy.optimize.minimize_scalar(
                fun=self._power_output, bounds=[-5.0, 0.0]
            )
            optimal_voltage = round(voltage_optimise_function.x, 3) * u.volt
            max_power = -voltage_optimise_function.fun * (
                u.watt / u.meter**2
            )  # Changed sign for minimize function to get maximize, now undo

            self.cache[cache_lookup] = (optimal_voltage, max_power)
        else:
            optimal_voltage, max_power = self.cache[cache_lookup]

        self.optimal_voltage: Final[u.Quantity] = optimal_voltage
        self.max_power: Final[u.Quantity] = max_power

    def _power_output(self, voltage: float):
        return -self._calculate_power_output_for_voltage(
            voltage=(round(voltage, 3) * u.volt),
            E_g=self.E_g,
            t_cell=self.t_cell,
            t_sky=self.t_sky,
        )

    def _calculate_power_output_for_voltage(
        self,
        voltage: u.Quantity,
        E_g: u.Quantity,
        t_sky: u.Quantity,
        t_cell: u.Quantity,
    ) -> float:
        chemical_potential_driving_emission: Final[u.Quantity] = voltage.value * u.eV
        power_output: Final[float] = (
            TotalPowerOutput(E_g=E_g)
            .get_total_power_output(
                voltage=voltage,
                t_sky=t_sky,
                t_cell=t_cell,
                chemical_potential_driving_emission=chemical_potential_driving_emission,
            )
            .value
        )
        return power_output
