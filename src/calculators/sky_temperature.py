from datetime import datetime
from typing import Final, Literal

from astropy import constants as const
from astropy import units as u

from src.api.copernicus_climate_data import CopernicusClimateData
from src.calculators.sky_emissivity import SkyEmissivity


class SkyTemperature:
    def __init__(
        self, surface_temperature_obj: CopernicusClimateData, lat: float, lon: float
    ):
        """https://doi.org/10.3390/app10228057"""
        self.surface_temperature_obj: Final[
            CopernicusClimateData
        ] = surface_temperature_obj
        self.lat: Final[float] = lat
        self.lon: Final[float] = lon

    def get_sky_temperature(
        self,
        date: datetime,
        formula: Literal["swinbank", "cloudy_sky", "martin-berdahl"],
    ) -> u.Quantity:
        t_ambient: Final[u.Quantity] = self._get_2m_temperature(date=date)
        match formula:
            case "martin-berdahl":
                sky_emissivity: Final[float] = SkyEmissivity(
                    method="martin-berdahl",
                    date=date,
                    surface_temperature_obj=self.surface_temperature_obj,
                    lat=self.lat,
                    lon=self.lon,
                ).sky_emissivity

                t_sky: Final[u.Quantity] = (
                    (sky_emissivity**0.25) * t_ambient * u.Kelvin
                )
                return t_sky.value * u.K

            case "cloudy_sky":
                """https://www.mdpi.com/2076-3417/10/22/8057"""
                horizontal_net_infrared_radiation_downwards: Final[
                    u.Quantity
                ] = self._get_horizontal_net_infrared_radiation_downwards_per_second(
                    date=date
                )

                return (
                    horizontal_net_infrared_radiation_downwards / const.sigma_sb
                ) ** (1 / 4)
            case "swinbank":
                """Swinbank's formula, assuming use during the night.
                (0020-0891, Infrared Phys Vol. 29 No. 2-4 pp. 231-232, 1989),
                243615948_The_sky_temperature_in_net_radiant_heat_loss_calculations_from_low-sloped_roofs
                """
                return (
                    0.0553 * t_ambient.value**1.5
                ) * u.Kelvin  # DOI: 10.1016/0020-0891(89)90055-9
            case _:
                raise ValueError(
                    "Formula not in defined formulae for sky temperature", formula
                )

    def _get_2m_temperature(self, date: datetime) -> u.Quantity:
        return self.surface_temperature_obj.get_2m_temperature(
            date=date, lat=self.lat, lon=self.lon
        )

    def _get_horizontal_net_infrared_radiation_downwards_per_second(
        self, date: datetime
    ) -> u.Quantity:
        return self.surface_temperature_obj.get_downwards_thermal_radiation(
            date=date, convert_to_watts=True, lat=self.lat, lon=self.lon
        )
