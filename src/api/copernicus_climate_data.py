import math
import os
import pathlib
from datetime import datetime
from typing import Final, Literal

import cdsapi
import numpy as np
import xarray as xr
from astropy import units as u


class CopernicusClimateData:
    def __init__(self, lon: float, lat: float, year: int, months: list[int]):
        self.c: Final[cdsapi.Client] = cdsapi.Client()

        required_dataset_shortnames: Final[list[str]] = [
            "skt",
            "d2m",
            "tcc",
            "strd",
            "t2m",
            "cbh",
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

            filepath: str = self._generate_filepath(
                dataset_shortname=dataset_shortname,
                lon_min=lon_min,
                lon_max=lon_max,
                lat_min=lat_min,
                lat_max=lat_max,
                year=year,
                month=month,
            )
            if os.path.isfile(filepath):
                print(f"Already exists at {filepath}!")
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
        is_data_nested = True if dataset_shortname in {"cbh"} else False

        hour_str = str(date.hour) if date.hour >= 10 else f"0{date.hour}"
        day_str = str(date.day) if date.day >= 10 else f"0{date.day}"
        month_str = str(date.month) if date.month >= 10 else f"0{date.month}"

        try:
            index_in_dataset: int
            index_difference: int | None = None
            match is_data_nested:
                case False:
                    index_in_dataset = date.hour + date.day * 24 - 24
                case True:
                    dataset_dates: Final[np.ndarray] = (
                        self.temperature_datasets[(date.month, dataset_shortname)]
                        .sel(latitude=self.lat, longitude=self.lon, method="nearest")
                        .coords["time"]
                        .values
                    )

                    if np.datetime64(date) in dataset_dates:
                        previous_dataset_date = np.datetime64(date)
                        index_difference = 0
                    else:
                        previous_dataset_date = min(
                            item for item in dataset_dates if item > np.datetime64(date)
                        )
                        index_difference = round(
                            (np.datetime64(date) - previous_dataset_date)
                            / np.timedelta64(1, "h")
                        )

                    index_in_dataset = np.where(previous_dataset_date == dataset_dates)[
                        0
                    ][0]
                case _:
                    raise ValueError("Case must be boolean", is_data_nested)

            if is_data_nested:
                """two lookups required"""
                if index_difference is None:
                    raise ValueError("index_difference not set")

                return (
                    self.temperature_datasets[(date.month, dataset_shortname)][
                        dataset_shortname
                    ]
                    .sel(latitude=self.lat, longitude=self.lon, method="nearest")
                    .values[index_in_dataset][index_difference]
                )
            elif self.temperature_datasets[(date.month, dataset_shortname)].sel(
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
                raise ValueError(
                    "Date does not correspond to expected", dataset_shortname, str(date)
                )

        except IndexError as e:
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
                raise ValueError("Date does not correspond to expected") from e

    def get_average_value_from_dataset(
        self, dataset_shortname: str, date: datetime, period: Literal["month"]
    ) -> float:
        match period:
            case "month":
                result: Final[float] = float(
                    np.nanmean(
                        self.temperature_datasets[(date.month, dataset_shortname)][
                            dataset_shortname
                        ]
                        .sel(latitude=self.lat, longitude=self.lon, method="nearest")
                        .values
                    )
                )
                return result
            case _:
                raise ValueError("Unknown period", period)

    def get_2m_temperature(self, date: datetime) -> u.Quantity:
        return (
            self.get_value_from_dataset(dataset_shortname="t2m", date=date) * u.Kelvin
        )

    def get_cloud_base_height(self, date: datetime) -> u.Quantity:
        return self.get_value_from_dataset(dataset_shortname="cbh", date=date) * u.meter

    def get_surface_temperature(self, date: datetime) -> u.Quantity:
        return (
            self.get_value_from_dataset(dataset_shortname="skt", date=date) * u.Kelvin
        )

    def get_downwards_thermal_radiation(
        self, date: datetime, convert_to_watts: bool = False
    ) -> u.Quantity:
        downwards_thermal_radiation: Final[float] = self.get_value_from_dataset(
            dataset_shortname="strd", date=date
        )
        if convert_to_watts:
            return (downwards_thermal_radiation / (60 * 60)) * (u.watt / u.meter**2)
        return downwards_thermal_radiation * (u.Joule / u.meter**2)

    def get_2metre_dewpoint_temperature_hourly(self, date: datetime) -> u.Quantity:
        return (
            self.get_value_from_dataset(dataset_shortname="d2m", date=date) * u.Kelvin
        )

    def get_2metre_dewpoint_temperature_monthly_average(
        self, date: datetime
    ) -> u.Quantity:
        return (
            self.get_average_value_from_dataset(
                dataset_shortname="d2m", date=date, period="month"
            )
            * u.Kelvin
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
        return os.path.abspath(
            f"data/era5_{dataset_shortname}/{year}/{month}/{lat_min}_{lat_max}_{lon_min}_{lon_max}/download.grib"
        ).replace(
            "radiative-power-output-prediction/tests/data/",
            "radiative-power-output-prediction/data/",
        )

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
            "strd": "surface_thermal_radiation_downwards",
            "cbh": "cloud_base_height",
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
        if variable_shortname in {"tcc", "2t", "t2m", "cbh"}:
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
