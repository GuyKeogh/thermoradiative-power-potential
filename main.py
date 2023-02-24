import json
import os.path
from datetime import datetime, timedelta
from typing import Final

import pandas as pd
from astropy import units as u

from src.api.copernicus_climate_data import CopernicusClimateData
from src.calculators.coordinates_for_assessment import get_coordinates_for_assessment
from src.calculators.maximum_power_point_tracker import MaximumPowerPointTracker
from src.calculators.sky_temperature import SkyTemperature
from src.dates import get_hourly_datetimes_between_period


def get_test_power_output():
    t_surf = 300 * u.Kelvin
    t_sky = 270 * u.Kelvin
    semiconductor_bandgap: Final[u.Quantity] = 0.1 * u.electronvolt

    power_output = MaximumPowerPointTracker(
        t_cell=t_surf, t_sky=t_sky, E_g=semiconductor_bandgap
    ).get_max_power()
    power_output = MaximumPowerPointTracker(
        t_cell=t_surf, t_sky=t_sky, E_g=semiconductor_bandgap
    ).get_max_power()
    print(
        f"Surface temperature = {t_surf} and sky temperature = {t_sky}.\nPower output = {power_output.value}W"
    )


def process_batch() -> None:
    batch_quantity: Final[int] = 10
    batch_start: Final[int] = 0
    batch_start_plus_quantity: Final[int] = batch_start + batch_quantity

    start_date: Final[datetime] = datetime(2022, 1, 1)
    end_date: Final[datetime] = datetime(2022, 12, 31)

    coordinates_for_assessment: Final[
        list[tuple[float, float]]
    ] = get_coordinates_for_assessment()

    batch_end = (
        batch_start_plus_quantity
        if batch_start_plus_quantity <= len(coordinates_for_assessment)
        else len(coordinates_for_assessment)
    )
    for lon, lat in coordinates_for_assessment[batch_start:batch_end]:
        print(f"Processing co-ordinate lon:{lon}, lat:{lat}")
        save_power_output_between_dates(
            lon=lon, lat=lat, start_date=start_date, end_date=end_date
        )


def save_power_output_between_dates(
    lon: float, lat: float, start_date: datetime, end_date: datetime
):
    # lat = 53.5
    # lon = -6.5
    output_dir: Final[str] = os.path.abspath(
        f"data/out/{start_date.strftime('%Y%m%d-%H%M%S')}_{end_date.strftime('%Y%m%d-%H%M%S')}/{lat}_{lon}/"
    )
    os.makedirs(output_dir, exist_ok=True)

    surface_temperature_obj: Final[CopernicusClimateData] = CopernicusClimateData(
        lon=lon,
        lat=lat,
        year=start_date.year,
        months=[*range(start_date.month, end_date.month + 1)],
    )

    dt_power_dict: dict[datetime, u.Quantity] = dict()
    semiconductor_bandgap: Final[u.Quantity] = 0.17 * u.electronvolt

    total_kwh: float = 0.0
    for dt in get_hourly_datetimes_between_period(
        start_date=start_date, end_date=end_date
    ):
        t_surf: u.Quantity = surface_temperature_obj.get_surface_temperature(date=dt)
        t_sky: u.Quantity = SkyTemperature(
            surface_temperature_obj=surface_temperature_obj
        ).get_sky_temperature(date=dt, formula="martin-berdahl")

        mpp_object = MaximumPowerPointTracker(
            E_g=semiconductor_bandgap,
            t_sky=t_sky,
            t_cell=t_surf,
        )
        power_output = mpp_object.get_max_power()
        print(
            f"Produced {power_output} at optimal voltage of {mpp_object.get_optimal_voltage()}"
        )

        power_output = power_output.value
        if power_output > 0:
            total_kwh += power_output / 1000

        dt_power_dict[dt] = power_output

        print(
            f"For {dt}, surface temperature = {t_surf} and sky temperature = {t_sky}.\nPower output = {power_output}W"
        )

    dt_power_df: Final[pd.DataFrame] = pd.DataFrame.from_dict(
        data=dt_power_dict, orient="index", columns=["average_power_watts"]
    )
    dt_power_df.to_csv(os.path.join(output_dir, "power_output_per_dt.csv"))
    with open(os.path.join(output_dir, "json_data.json"), "w") as outfile:
        json.dump({"total_kwh_per_square_m": total_kwh}, outfile)
    """
    PowerOutputPlot().plot_output_vs_datetime(
        datetimes=dt_power_df.index, power_output=dt_power_df.power
    )
    """

    print(
        f"total kwh between {start_date} and {end_date + timedelta(hours=23)}: {total_kwh} kWh"
    )


if __name__ == "__main__":
    # get_test_power_output()
    # save_power_output_between_dates()
    process_batch()
