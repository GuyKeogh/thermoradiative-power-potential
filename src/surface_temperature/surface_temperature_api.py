import math
import os
import pathlib
from datetime import datetime
from typing import Final

import cdsapi
import numpy as np
import xarray as xr


class SurfaceTemperature:
    def __init__(self, lon: float, lat: float, year: int, month: int):
        self.c = cdsapi.Client()

        lon_min: Final[int] = math.floor(lon)
        lon_max: Final[int] = math.ceil(lon)
        lat_min: Final[int] = math.floor(lat)
        lat_max: Final[int] = math.ceil(lat)

        filepath: Final[str] = os.path.abspath(
            self._generate_filepath(
                lon_min=lon_min,
                lon_max=lon_max,
                lat_min=lat_min,
                lat_max=lat_max,
                year=year,
                month=month,
            )
        )
        if os.path.isfile(filepath):
            print("Already exists!")
        else:
            print("File doesn't exist! Downloading...")
            self._download_surface_temperature_file_for_month_for_region(
                filepath=filepath,
                lon_min=lon_min,
                lon_max=lon_max,
                lat_min=lat_min,
                lat_max=lat_max,
                year=year,
                month=month,
            )
        self.temperature_dataset: Final[xr.Dataset] = xr.open_dataset(
            filepath, engine="cfgrib"
        )

    def get_temperature(self, lon: float, lat: float, date: datetime) -> float:
        hour_str = str(date.hour) if date.hour >= 10 else f"0{date.hour}"
        day_str = str(date.day) if date.day >= 10 else f"0{date.day}"
        month_str = str(date.month) if date.month >= 10 else f"0{date.month}"
        if self.temperature_dataset["skt"].sel(
            latitude=lat, longitude=lon, method="nearest"
        ).coords["time"][date.hour + date.day * 24 - 24] == np.datetime64(
            f"{date.year}-{month_str}-{day_str}T{hour_str}:00"
        ):
            t_surface: float = (
                self.temperature_dataset["skt"]
                .sel(latitude=lat, longitude=lon, method="nearest")
                .values[date.hour]
            )
        else:
            raise ValueError("Date does not correspond to expected")
        print(f"Got temperature {t_surface}K at {date}")
        return t_surface

    def _generate_filepath(
        self,
        lon_min: int,
        lon_max: int,
        lat_min: int,
        lat_max: int,
        year: int,
        month: int,
    ) -> str:
        return f"data/surface_temperature/{year}/{month}/{lat_min}_{lat_max}_{lon_min}_{lon_max}/download.grib"

    def _download_surface_temperature_file_for_month_for_region(
        self,
        filepath: str,
        lon_min: int,
        lon_max: int,
        lat_min: int,
        lat_max: int,
        year: int,
        month: int,
    ) -> None:
        os.makedirs(pathlib.Path(filepath).parent, exist_ok=True)
        self.c.retrieve(
            "reanalysis-era5-land",
            {
                "variable": "skin_temperature",
                "year": str(year),
                "month": str(month),
                "day": [
                    "01",
                    "02",
                    "03",
                    "04",
                    "05",
                    "06",
                    "07",
                    "08",
                    "09",
                    "10",
                    "11",
                    "12",
                    "13",
                    "14",
                    "15",
                    "16",
                    "17",
                    "18",
                    "19",
                    "20",
                    "21",
                    "22",
                    "23",
                    "24",
                    "25",
                    "26",
                    "27",
                    "28",
                    "29",
                    "30",
                    "31",
                ],
                "time": [
                    "00:00",
                    "01:00",
                    "02:00",
                    "03:00",
                    "04:00",
                    "05:00",
                    "06:00",
                    "07:00",
                    "08:00",
                    "09:00",
                    "10:00",
                    "11:00",
                    "12:00",
                    "13:00",
                    "14:00",
                    "15:00",
                    "16:00",
                    "17:00",
                    "18:00",
                    "19:00",
                    "20:00",
                    "21:00",
                    "22:00",
                    "23:00",
                ],
                "format": "grib",
                "area": [
                    lat_max,
                    lon_min,
                    lat_min,
                    lon_max,
                ],
            },
            filepath,
        )

    def _download_surface_temperature_file(
        self, lon_min: int, lon_max: int, lat_min: int, lat_max: int, year: int
    ):
        grib_file = self.c.retrieve(
            "reanalysis-era5-land",
            {
                "year": "2023",
                "variable": "skin_temperature",
                "month": "01",
                "day": "30",
                "time": "01:00",
                "format": "grib",
            },
            "download.grib",
        )
