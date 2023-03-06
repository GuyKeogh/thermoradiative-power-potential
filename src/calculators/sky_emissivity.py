import math
from datetime import datetime
from typing import Final, Literal

import numpy as np
from astropy import units as u

from src.api.copernicus_climate_data import CopernicusClimateData
from src.exceptions import InsufficientClimateDataError, UnitError


class SkyEmissivity:
    def __init__(
        self,
        method: Literal["martin-berdahl"],
        date: datetime,
        surface_temperature_obj: CopernicusClimateData,
        lat: float,
        lon: float,
    ):
        self.surface_temperature_obj: Final[
            CopernicusClimateData
        ] = surface_temperature_obj
        self.lat: Final[float] = lat
        self.lon: Final[float] = lon

        sky_emissivity: float
        match method:
            case "martin-berdahl":
                sky_emissivity = self._get_emissivity_via_martin_berdahl_method(
                    date=date
                )
            case _:
                raise ValueError("Unknown sky emissivity method", method)
        self.sky_emissivity: Final[float] = sky_emissivity

    def _get_emissivity_via_martin_berdahl_method(self, date: datetime) -> float:
        """https://publications.ibpsa.org/proceedings/bs/2017/papers/BS2017_569.pdf"""
        t_dewpoint_monthly_average: Final[float] = (
            self._get_dewpoint_temperature(date=date, period="month")
            .to(unit=u.deg_C, equivalencies=u.temperature())
            .value
        )
        surface_pressure_mbar: Final[u.Quantity] = self._get_surface_pressure(
            date=date
        ).to(u.mbar)

        emissivity_monthly: Final[float] = (
            0.711
            + 0.56 * (t_dewpoint_monthly_average / 100)
            + 0.73 * (t_dewpoint_monthly_average / 100) ** 2
        )
        emissivity_hourly_diurnal_correction: Final[float] = 0.013 * math.cos(
            2 * math.pi * ((date.hour + 1) / 24)
        )

        emissivity_elevation_correction: float = 0.0
        if not np.isnan(surface_pressure_mbar):
            emissivity_elevation_correction = 0.00012 * (
                surface_pressure_mbar.value - 1000
            )
        else:
            print("surface_pressure was NaN")

        emissivity_clearsky: Final[float] = (
            emissivity_monthly
            + emissivity_hourly_diurnal_correction
            + emissivity_elevation_correction
        )

        cloud_base_height: Final[u.Quantity] = self._get_cloud_base_height(date=date)
        if cloud_base_height.unit != u.meter:
            raise UnitError("Cloud base height must be in meters")

        if not math.isnan(cloud_base_height.value):
            cloud_base_temperature_factor: Final[float] = math.exp(
                -cloud_base_height.value / 8200
            )
            fractional_sky_cover: Final[float] = self._get_opaque_sky_cover(date=date)

            infrared_cloud_amount: Final[float] = (
                fractional_sky_cover
                * emissivity_clearsky
                * cloud_base_temperature_factor
            )

            emissivity_sky: float = (
                emissivity_clearsky + (1 - emissivity_clearsky) * infrared_cloud_amount
            )
        else:  # assumption
            emissivity_sky = emissivity_clearsky
        if emissivity_sky < 0 or emissivity_sky > 1:
            raise ValueError(
                "Sky emissivity must be greater than 0 and less than 1",
                emissivity_sky,
            )
        if np.isnan(emissivity_sky):
            raise InsufficientClimateDataError("Emissivity cannot be NaN")
        return emissivity_sky

    def _get_dewpoint_temperature(
        self, date: datetime, period: Literal["month", "hour"] = "hour"
    ) -> u.Quantity:
        match period:
            case "hour":
                return (
                    self.surface_temperature_obj.get_2metre_dewpoint_temperature_hourly(
                        date=date, lat=self.lat, lon=self.lon
                    )
                )
            case "month":
                return self.surface_temperature_obj.get_2metre_dewpoint_temperature_monthly_average(
                    date=date, lat=self.lat, lon=self.lon
                )
            case _:
                raise ValueError("Unknown period", period)

    def _get_opaque_sky_cover(self, date: datetime) -> float:
        """opaque sky cover (tenths)"""
        sky_cover: Final[int] = round(
            self.surface_temperature_obj.get_total_cloud_cover(
                date=date, lat=self.lat, lon=self.lon
            )
        )

        if sky_cover < 0 or sky_cover > 1:
            raise ValueError(
                f"Sky cover must be greater than 0 and less than 1 ({sky_cover})"
            )
        return sky_cover

    def _get_cloud_base_height(self, date: datetime) -> u.Quantity:
        return self.surface_temperature_obj.get_cloud_base_height(
            date=date, lat=self.lat, lon=self.lon
        )

    def _get_surface_pressure(self, date: datetime) -> u.Quantity:
        return self.surface_temperature_obj.get_surface_pressure(
            date=date, lat=self.lat, lon=self.lon
        )
