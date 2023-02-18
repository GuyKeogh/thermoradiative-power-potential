import math
from datetime import datetime
from typing import Final

from astropy import units as u

from src.api.surface_temperature_api import SurfaceTemperature
from src.exceptions import UnitError


class SkyTemperature:
    def __init__(self, surface_temperature_obj: SurfaceTemperature):
        """https://doi.org/10.3390/app10228057"""
        self.surface_temperature_obj: Final[
            SurfaceTemperature
        ] = surface_temperature_obj

    def get_sky_temperature(self, date: datetime) -> u.Quantity:
        """
        Use Swinbank's formula, assuming use during the night. (0020-0891, Infrared Phys Vol. 29 No. 2-4 pp. 231-232, 1989), https://www.researchgate.net/publication/243615948_The_sky_temperature_in_net_radiant_heat_loss_calculations_from_low-sloped_roofs
        Alternatively try: https://www.mdpi.com/2076-3417/10/22/8057
        """

        # horizontal_net_infrared_radiation_downwards: Final[u.Quantity] = self._get_horizontal_net_infrared_radiation_downwards_per_second(date=date)

        # return (horizontal_net_infrared_radiation_downwards/const.sigma_sb) ** (1/4)

        t_ambient: Final[u.Quantity] = self._get_2m_temperature(date=date)
        return (
            0.0553 * t_ambient**1.5
        ).value * u.Kelvin  # DOI: 10.1016/0020-0891(89)90055-9

    def _get_2m_temperature(self, date: datetime) -> u.Quantity:
        return self.surface_temperature_obj.get_2m_temperature(date=date)

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
        N: Final[int] = self._get_opaque_sky_cover(date=date)

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

    def _get_opaque_sky_cover(self, date: datetime) -> int:
        """opaque sky cover (tenths), where sky cover: the expected amount of opaque clouds covering
        the sky valid for the indicated hour where N equals 0 for clear sky and 10 for overcast sky
        """
        sky_cover: Final[int] = round(
            self.surface_temperature_obj.get_total_cloud_cover(date=date) * 10
        )

        if sky_cover < 0 or sky_cover > 10:
            raise ValueError(
                f"Sky cover must be greater than 0 and less than 10 ({sky_cover})"
            )
        return sky_cover

    def _get_dewpoint_temperature(self, date: datetime) -> u.Quantity:
        return self.surface_temperature_obj.get_2metre_dewpoint_temperature(date=date)
