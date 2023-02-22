import math
from datetime import datetime
from typing import Final, Literal

from astropy import constants as const
from astropy import units as u

from src.api.copernicus_climate_data import CopernicusClimateData
from src.exceptions import UnitError


class SkyTemperature:
    def __init__(self, surface_temperature_obj: CopernicusClimateData):
        """https://doi.org/10.3390/app10228057"""
        self.surface_temperature_obj: Final[
            CopernicusClimateData
        ] = surface_temperature_obj

    def get_sky_temperature(
        self,
        date: datetime,
        formula: Literal["swinbank", "cloudy_sky", "martin-berdahl"],
    ) -> u.Quantity:
        t_ambient: Final[u.Quantity] = self._get_2m_temperature(date=date)
        # t_dewpoint: Final[u.Quantity] = self._get_dewpoint_temperature(date=date, period="hour")
        match formula:
            case "martin-berdahl":
                t_dewpoint_monthly_average: Final[float] = (
                    self._get_dewpoint_temperature(date=date, period="month")
                    .to(unit=u.deg_C, equivalencies=u.temperature())
                    .value
                )
                """https://publications.ibpsa.org/proceedings/bs/2017/papers/BS2017_569.pdf"""
                emissivity_monthly: Final[float] = (
                    0.711
                    + 0.56 * (t_dewpoint_monthly_average / 100)
                    + 0.73 * (t_dewpoint_monthly_average / 100) ** 2
                )
                emissivity_hourly_diurnal_correction: Final[float] = 0.013 * math.cos(
                    2 * math.pi * (date.hour / 24)
                )
                emissivity_clearsky: Final[float] = (
                    emissivity_monthly + emissivity_hourly_diurnal_correction
                )

                cloud_base_height: Final[u.Quantity] = self._get_cloud_base_height(
                    date=date
                )
                if cloud_base_height.unit != u.meter:
                    raise UnitError("Cloud base height must be in meters")

                if not math.isnan(cloud_base_height.value):
                    cloud_amount: Final[float] = math.exp(
                        -cloud_base_height.value / 8200
                    )
                    fractional_sky_cover: Final[float] = self._get_opaque_sky_cover(
                        date=date
                    )
                    cloud_emissivity: Final[float] = (
                        0.4 if fractional_sky_cover < 0.5 else 1.0
                    )

                    infrared_cloud_amount: Final[float] = (
                        fractional_sky_cover * cloud_emissivity * cloud_amount
                    )

                    emissivity_sky: Final[float] = (
                        emissivity_clearsky
                        + (1 - emissivity_clearsky) * infrared_cloud_amount
                    )
                else:  # assumption
                    emissivity_sky = emissivity_clearsky
                if emissivity_sky < 0 or emissivity_sky > 1:
                    raise ValueError(
                        "Sky emissivity must be greater than 0 and less than 1",
                        emissivity_sky,
                    )

                t_sky: Final[u.Quantity] = (
                    (emissivity_sky**0.25) * t_ambient * u.Kelvin
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
                """Swinbank's formula, assuming use during the night. (0020-0891, Infrared Phys Vol. 29 No. 2-4 pp. 231-232, 1989), https://www.researchgate.net/publication/243615948_The_sky_temperature_in_net_radiant_heat_loss_calculations_from_low-sloped_roofs"""
                return (
                    0.0553 * t_ambient.value**1.5
                ) * u.Kelvin  # DOI: 10.1016/0020-0891(89)90055-9
            case _:
                raise ValueError(
                    "Formula not in defined formulae for sky temperature", formula
                )

    def _get_2m_temperature(self, date: datetime) -> u.Quantity:
        return self.surface_temperature_obj.get_2m_temperature(date=date)

    def _get_cloud_base_height(self, date: datetime) -> u.Quantity:
        return self.surface_temperature_obj.get_cloud_base_height(date=date)

    def _get_horizontal_net_infrared_radiation_downwards_per_second(
        self, date: datetime
    ) -> u.Quantity:
        return self.surface_temperature_obj.get_downwards_thermal_radiation(
            date=date, convert_to_watts=True
        )

    def _get_sky_emissivity(self, date: datetime) -> float:
        """https://doi.org/10.3390/app10228057 eqn 2"""
        dewpoint_temperature: Final[u.Quantity] = self._get_dewpoint_temperature(
            date=date
        )
        N: Final[float] = self._get_opaque_sky_cover(date=date)

        if dewpoint_temperature.unit != u.Kelvin:
            raise UnitError(
                "Emissivity equation requires dewpoint_temperature in Kelvin",
                dewpoint_temperature.unit,
            )
        emissivity: Final[float] = (
            (0.787 + (0.767 * math.log(dewpoint_temperature.value / 273)))
            + 0.0224 * N
            - 0.0035 * N**2
            + 0.00028 * N**3
        )

        if emissivity < 0 or emissivity > 1:
            raise ValueError(
                f"Emissivity must be less than 1 and greater than 0", emissivity
            )
        return emissivity

    def _get_opaque_sky_cover(self, date: datetime) -> float:
        """opaque sky cover (tenths)"""
        sky_cover: Final[int] = round(
            self.surface_temperature_obj.get_total_cloud_cover(date=date)
        )

        if sky_cover < 0 or sky_cover > 1:
            raise ValueError(
                f"Sky cover must be greater than 0 and less than 1 ({sky_cover})"
            )
        return sky_cover

    def _get_dewpoint_temperature(
        self, date: datetime, period: Literal["month", "hour"] = "hour"
    ) -> u.Quantity:
        match period:
            case "hour":
                return (
                    self.surface_temperature_obj.get_2metre_dewpoint_temperature_hourly(
                        date=date
                    )
                )
            case "month":
                return self.surface_temperature_obj.get_2metre_dewpoint_temperature_monthly_average(
                    date=date
                )
            case _:
                raise ValueError("Unknown period", period)
