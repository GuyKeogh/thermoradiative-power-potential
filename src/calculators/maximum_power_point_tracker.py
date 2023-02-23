from decimal import Decimal
from typing import Final

import numpy as np
from astropy import units as u

from src.calculators.total_power_output import TotalPowerOutput


class MaximumPowerPointTracker:
    def __init__(
        self,
        t_sky: u.Quantity,
        t_cell: u.Quantity,
        E_g: u.Quantity,
    ):
        self.t_sky: Final[u.Quantity] = t_sky
        self.t_cell: Final[u.Quantity] = t_cell
        self.E_g: Final[u.Quantity] = E_g

        voltage_to_power_dict: dict[Decimal, u.Quantity] = dict()
        voltage_range: Final[np.ndarray] = np.arange(
            start=-0.04, stop=-0.01, step=0.001
        )
        voltage: float
        for voltage in voltage_range:
            voltage_decimal: Decimal = Decimal(voltage).quantize(Decimal(".001"))
            voltage_to_power_dict[
                voltage_decimal
            ] = self._calculate_power_output_for_voltage(
                voltage=(voltage_decimal * u.volt)
            )

        self.voltage_to_power_dict: Final[
            dict[Decimal, u.Quantity]
        ] = voltage_to_power_dict

    def _calculate_power_output_for_voltage(self, voltage: u.Quantity) -> u.Quantity:
        chemical_potential_driving_emission: Final[u.Quantity] = voltage.value * u.eV
        return TotalPowerOutput(E_g=self.E_g).get_total_power_output(
            voltage=voltage,
            t_sky=self.t_sky,
            t_cell=self.t_cell,
            chemical_potential_driving_emission=chemical_potential_driving_emission,
        )

    def get_max_power(self) -> u.Quantity:
        return max(self.voltage_to_power_dict.values()).value * (u.watt / u.meter**2)

    def get_optimal_voltage(self) -> u.Quantity:
        return (
            max(self.voltage_to_power_dict, key=self.voltage_to_power_dict.get) * u.volt
        )
