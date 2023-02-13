import math
import os
import pathlib
from datetime import datetime
from typing import Final

import cdsapi
import numpy as np
import xarray as xr
from astropy import units as u


class SurfaceTemperature:
    def __init__(self, lon: float, lat: float, year: int, months: list[int]):
        self.c = cdsapi.Client()

        required_dataset_shortnames: Final[list[str]] = ["skt"]

        lon_min: Final[int] = math.floor(lon)
        lon_max: Final[int] = math.ceil(lon)
        lat_min: Final[int] = math.floor(lat)
        lat_max: Final[int] = math.ceil(lat)

        self.temperature_datasets: [tuple[int, str], xr.Dataset] = dict()
        month: int
        iterator = [(f, s) for f in months for s in required_dataset_shortnames]
        for month, dataset_shortname in iterator:
            print(f"Downloading for month {month} and shortname {dataset_shortname}")

            filepath: str = os.path.abspath(
                self._generate_filepath(
                    dataset_shortname=dataset_shortname,
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
                    dataset_shortname=dataset_shortname,
                    lon_min=lon_min,
                    lon_max=lon_max,
                    lat_min=lat_min,
                    lat_max=lat_max,
                    year=year,
                    month=month,
                )
            temperature_dataset: xr.Dataset = xr.open_dataset(filepath, engine="cfgrib")
            self.temperature_datasets[(month, dataset_shortname)] = temperature_dataset

    def get_value_from_dataset(
        self, dataset_shortname: str, lon: float, lat: float, date: datetime
    ) -> float:
        hour_str = str(date.hour) if date.hour >= 10 else f"0{date.hour}"
        day_str = str(date.day) if date.day >= 10 else f"0{date.day}"
        month_str = str(date.month) if date.month >= 10 else f"0{date.month}"
        index_in_dataset: Final[int] = date.hour + date.day * 24 - 24

        if self.temperature_datasets[(date.month, dataset_shortname)].sel(
            latitude=lat, longitude=lon, method="nearest"
        ).coords["time"][index_in_dataset] == np.datetime64(
            f"{date.year}-{month_str}-{day_str}T{hour_str}:00"
        ):
            return (
                self.temperature_datasets[(date.month, dataset_shortname)][
                    dataset_shortname
                ]
                .sel(latitude=lat, longitude=lon, method="nearest")
                .values[index_in_dataset]
            )
        else:
            raise ValueError("Date does not correspond to expected")

    def get_surface_temperature(
        self, lon: float, lat: float, date: datetime
    ) -> float | u.Quantity:
        t_surface: Final[float] = self.get_value_from_dataset(
            dataset_shortname="skt", lon=lon, lat=lat, date=date
        )
        print(f"Got temperature {t_surface}K at {date}")
        return t_surface * u.Kelvin

    def get_downwards_thermal_radiation(
        self, lon: float, lat: float, date: datetime
    ) -> float | u.Quantity:
        downwards_thermal_radiation: Final[float] = self.get_value_from_dataset(
            dataset_shortname="strd", lon=lon, lat=lat, date=date
        )
        print(
            f"Got downwards thermal radiation {downwards_thermal_radiation}Jm^(-2) at {date}"
        )
        return downwards_thermal_radiation * (u.Joule / u.metre**2)

    def _generate_filepath(
        self,
        dataset_shortname: str,
        lon_min: int,
        lon_max: int,
        lat_min: int,
        lat_max: int,
        year: int,
        month: int,
    ) -> str:
        return f"data/era5_{dataset_shortname}/{year}/{month}/{lat_min}_{lat_max}_{lon_min}_{lon_max}/download.grib"

    def _download_surface_temperature_file_for_month_for_region(
        self,
        filepath: str,
        dataset_shortname: str,
        lon_min: int,
        lon_max: int,
        lat_min: int,
        lat_max: int,
        year: int,
        month: int,
    ) -> None:
        dataset_shortname_to_variable_name_dict: Final[dict[str, str]] = dict(
            skt="skin_temperature", strd="surface_thermal_radiation_downwards"
        )

        os.makedirs(pathlib.Path(filepath).parent, exist_ok=True)
        self.c.retrieve(
            "reanalysis-era5-land",
            {
                "variable": dataset_shortname_to_variable_name_dict[dataset_shortname],
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
