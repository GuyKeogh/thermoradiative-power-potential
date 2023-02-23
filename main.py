from datetime import datetime, timedelta
from typing import Final

import pandas as pd

# from src.calculators.electric_potential import get_semiconductor_electric_potential
from astropy import constants as const
from astropy import units as u

from src.api.copernicus_climate_data import CopernicusClimateData
from src.calculators.maximum_power_point_tracker import MaximumPowerPointTracker
from src.calculators.sky_temperature import SkyTemperature
from src.calculators.total_power_output import TotalPowerOutput
from src.constants import Characteristics_HgCdZnTe
from src.dates import get_hourly_datetimes_between_period
from src.plots.power_output import PowerOutputPlot


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


def get_power_output_between_dates():
    lat = 53.3608909
    lon = -6.3061867

    start_date: Final[datetime] = datetime(2022, 1, 1)
    end_date: Final[datetime] = datetime(2022, 1, 31)
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
        data=dt_power_dict, orient="index", columns=["power"]
    )
    PowerOutputPlot().plot_output_vs_datetime(
        datetimes=dt_power_df.index, power_output=dt_power_df.power
    )

    print(
        f"total kwh between {start_date} and {end_date + timedelta(hours=23)}: {total_kwh} kWh"
    )


if __name__ == "__main__":
    # get_test_power_output()
    get_power_output_between_dates()
