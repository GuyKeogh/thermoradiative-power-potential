from decimal import Decimal
from functools import lru_cache
from typing import Final

import numpy as np
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
        voltage_to_power_dict: dict[Decimal, u.Quantity] = dict()
        voltage_range: Final[np.ndarray] = np.arange(
            start=-0.05, stop=-0.01, step=0.001
        )
        voltage: float
        for voltage in voltage_range:
            voltage_decimal: Decimal = Decimal(voltage).quantize(Decimal(".001"))
            voltage_to_power_dict[
                voltage_decimal
            ] = self._calculate_power_output_for_voltage(
                voltage=(voltage_decimal * u.volt),
                E_g=E_g,
                t_cell=t_cell,
                t_sky=t_sky,
            )

        self.voltage_to_power_dict: Final[
            dict[Decimal, u.Quantity]
        ] = voltage_to_power_dict
        self.voltage_with_max_power: Final[Decimal] = max(
            voltage_to_power_dict, key=lambda key: voltage_to_power_dict[key]
        )

    @classmethod
    @lru_cache(maxsize=None)
    def _calculate_power_output_for_voltage(
        self,
        voltage: u.Quantity,
        E_g: u.Quantity,
        t_sky: u.Quantity,
        t_cell: u.Quantity,
    ) -> u.Quantity:
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
            return power_output
        else:
            return self.cache[cache_lookup]

    def get_max_power(self) -> u.Quantity:
        return self.voltage_to_power_dict[self.voltage_with_max_power].value * (
            u.watt / u.meter**2
        )

    def get_optimal_voltage(self) -> u.Quantity:
        return self.voltage_with_max_power * u.volt
