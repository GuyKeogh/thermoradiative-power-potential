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

        required_dataset_shortnames: Final[list[str]] = [
            "skt",
            "d2m",
            "tcc",
            "strd",
            "t2m",
        ]

        self.lon: Final[float] = lon
        self.lat: Final[float] = lat

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
                    variable_shortname=dataset_shortname,
                    lon_min=lon_min,
                    lon_max=lon_max,
                    lat_min=lat_min,
                    lat_max=lat_max,
                    year=year,
                    month=month,
                )
            temperature_dataset: xr.Dataset = xr.open_dataset(filepath, engine="cfgrib")
            self.temperature_datasets[(month, dataset_shortname)] = temperature_dataset

    def get_value_from_dataset(self, dataset_shortname: str, date: datetime) -> float:
        hour_str = str(date.hour) if date.hour >= 10 else f"0{date.hour}"
        day_str = str(date.day) if date.day >= 10 else f"0{date.day}"
        month_str = str(date.month) if date.month >= 10 else f"0{date.month}"

        try:
            index_in_dataset: Final[int] = date.hour + date.day * 24 - 24
            if self.temperature_datasets[(date.month, dataset_shortname)].sel(
                latitude=self.lat, longitude=self.lon, method="nearest"
            ).coords["time"][index_in_dataset] == np.datetime64(
                f"{date.year}-{month_str}-{day_str}T{hour_str}:00"
            ):
                return (
                    self.temperature_datasets[(date.month, dataset_shortname)][
                        dataset_shortname
                    ]
                    .sel(latitude=self.lat, longitude=self.lon, method="nearest")
                    .values[index_in_dataset]
                )
            else:
                raise ValueError("Date does not correspond to expected")
        except IndexError:
            # data possibly given daily with steps
            if self.temperature_datasets[(date.month, dataset_shortname)].sel(
                latitude=self.lat, longitude=self.lon, method="nearest"
            ).coords["time"][date.day] == np.datetime64(
                f"{date.year}-{month_str}-{day_str}T00:00"
            ):
                return (
                    self.temperature_datasets[(date.month, dataset_shortname)][
                        dataset_shortname
                    ]
                    .sel(latitude=self.lat, longitude=self.lon, method="nearest")
                    .values[date.day][date.hour]
                )
            else:
                raise ValueError("Date does not correspond to expected")

    def get_2m_temperature(self, date: datetime) -> u.Quantity:
        t_surface: Final[float] = self.get_value_from_dataset(
            dataset_shortname="t2m", date=date
        )
        print(f"Got temperature {t_surface}K at {date}")
        return t_surface * u.Kelvin

    def get_surface_temperature(self, date: datetime) -> u.Quantity:
        t_surface: Final[float] = self.get_value_from_dataset(
            dataset_shortname="skt", date=date
        )
        print(f"Got temperature {t_surface}K at {date}")
        return t_surface * u.Kelvin

    def get_downwards_thermal_radiation(
        self, date: datetime, convert_to_watts: bool = False
    ) -> u.Quantity:
        downwards_thermal_radiation: Final[float] = self.get_value_from_dataset(
            dataset_shortname="strd", date=date
        )
        print(
            f"Got downwards thermal radiation {downwards_thermal_radiation}Jm^(-2) at {date}"
        )
        if convert_to_watts:
            return (downwards_thermal_radiation / (60 * 60)) * (u.watt / u.meter**2)
        return downwards_thermal_radiation * (u.Joule / u.meter**2)

    def get_2metre_dewpoint_temperature(self, date: datetime) -> u.Quantity:
        return (
            self.get_value_from_dataset(dataset_shortname="d2m", date=date) * u.Kelvin
        )

    def get_total_cloud_cover(self, date: datetime) -> float:
        return self.get_value_from_dataset(dataset_shortname="tcc", date=date)

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
        variable_shortname: str,
        lon_min: int,
        lon_max: int,
        lat_min: int,
        lat_max: int,
        year: int,
        month: int,
    ) -> None:
        os.makedirs(pathlib.Path(filepath).parent, exist_ok=True)
        dataset_shortname_to_variable_name_dict: Final[dict[str, str]] = {
            "skt": "skin_temperature",
            "d2m": "2m_dewpoint_temperature",
            "tcc": "total_cloud_cover",
            "t2m": "2m_temperature",
        }
        variable_longname: Final[str] = dataset_shortname_to_variable_name_dict[
            variable_shortname
        ]

        area_list: Final[list[int]] = [
            lat_max,
            lon_min,
            lat_min,
            lon_max,
        ]
        complete_day_list: Final[list[str]] = [
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
        ]
        complete_time_list: Final[list[str]] = [
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
        ]

        dataset: str = "reanalysis-era5-land"
        if variable_shortname in {"tcc", "2t"}:
            dataset = "reanalysis-era5-single-levels"

        request_arguments: dict[str, str | list[str | int]] = {
            "variable": variable_longname,
            "year": str(year),
            "month": str(month),
            "day": complete_day_list,
            "time": complete_time_list,
            "format": "grib",
            "area": area_list,
        }
        if dataset == "reanalysis-era5-single-levels":
            request_arguments["product_type"] = "reanalysis"

        try:
            self.c.retrieve(
                dataset,
                request_arguments,
                filepath,
            )
        except Exception:
            print(request_arguments)
            raise
