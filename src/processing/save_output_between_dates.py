import json
import os
from datetime import datetime, timedelta
from typing import Final, Literal

import numpy as np
import pandas as pd
from astropy import units as u

from src.api.copernicus_climate_data import CopernicusClimateData
from src.calculators.maximum_power_point_tracker import MaximumPowerPointTracker
from src.calculators.sky_temperature import SkyTemperature
from src.dates import get_hourly_datetimes_between_period
from src.exceptions import InsufficientClimateDataError


def save_power_output_between_dates(
    climate_data_obj: CopernicusClimateData,
    lon: float,
    lat: float,
    start_date: datetime,
    end_date: datetime,
    emissivity_method: Literal["swinbank", "martin-berdahl"],
):
    output_dir: Final[str] = os.path.abspath(
        f"data/out/{emissivity_method}/{start_date.strftime('%Y%m%d-%H%M%S')}_{end_date.strftime('%Y%m%d-%H%M%S')}/"
        f"{lat}_{lon}/"
    )
    os.makedirs(output_dir, exist_ok=True)

    dt_data_dict: dict[
        datetime, tuple[u.Quantity, u.Quantity, u.Quantity, u.Quantity]
    ] = dict()
    semiconductor_bandgap: Final[u.Quantity] = 0.17 * u.electronvolt

    total_kwh: float = 0.0
    for dt in get_hourly_datetimes_between_period(
        start_date=start_date, end_date=end_date
    ):
        t_surf: u.Quantity = climate_data_obj.get_surface_temperature(
            date=dt, lat=lat, lon=lon
        )
        t_sky: u.Quantity = SkyTemperature(
            surface_temperature_obj=climate_data_obj, lat=lat, lon=lon
        ).get_sky_temperature(date=dt, formula=emissivity_method)

        if np.isnan(t_surf) or np.isnan(t_sky):
            raise InsufficientClimateDataError(
                "Neither t_surf or t_sky may be NaN", t_surf, t_sky
            )

        mpp_object = MaximumPowerPointTracker(
            E_g=semiconductor_bandgap,
            t_sky=t_sky,
            t_cell=t_surf,
        )
        power_output = mpp_object.max_power
        optimal_voltage = mpp_object.optimal_voltage
        print(
            f"Produced {power_output} at optimal voltage of {mpp_object.optimal_voltage}"
        )

        power_output = power_output.value
        if power_output > 0:
            total_kwh += power_output / 1000

        dt_data_dict[dt] = (
            power_output,
            optimal_voltage.value,
            t_sky.value,
            t_surf.value,
        )

        print(
            f"For {dt}, surface temperature = {t_surf} and sky temperature = {t_sky}.\nPower output = {power_output}W"
        )

    dt_power_df: Final[pd.DataFrame] = pd.DataFrame.from_dict(
        data=dt_data_dict,
        orient="index",
        columns=["average_power_watts_per_sqm", "optimal_voltage", "t_sky", "t_surf"],
    )

    print(f"Saving to {output_dir}")
    dt_power_df.to_csv(os.path.join(output_dir, "data_per_dt.csv"))
    with open(os.path.join(output_dir, "json_data.json"), "w") as outfile:
        json.dump({"total_kwh_per_square_m": total_kwh}, outfile)

    print(
        f"total kwh between {start_date} and {end_date + timedelta(hours=23)}: {total_kwh} kWh"
    )
