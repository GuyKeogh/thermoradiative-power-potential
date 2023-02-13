from datetime import datetime, timedelta
from typing import Final

import pandas as pd
from astropy import units as u

from src.calculators.total_power_output import TotalPowerOutput
from src.constants import Characteristics_HgCdZnTe
from src.dates import get_hourly_datetimes_between_period
from src.plots.power_output import PowerOutputPlot
from src.surface_temperature.surface_temperature_api import SurfaceTemperature

if __name__ == "__main__":
    lat = 53.3608909
    lon = -6.3061867

    start_date: Final[datetime] = datetime(2022, 2, 27)
    end_date: Final[datetime] = datetime(2022, 2, 27)
    surface_temperature_obj: Final[SurfaceTemperature] = SurfaceTemperature(
        lon=lon,
        lat=lat,
        year=start_date.year,
        months=[*range(start_date.month, end_date.month + 1)],
    )

    dt_power_dict: dict[datetime, u.Quantity] = dict()

    total_kwh: float = 0.0
    for dt in get_hourly_datetimes_between_period(
        start_date=start_date, end_date=end_date
    ):
        temp: u.Quantity = surface_temperature_obj.get_surface_temperature(
            lon=lon, lat=lat, date=dt
        )

        power_output = TotalPowerOutput(
            E_g=0.01 * u.electronvolt
        ).get_extractible_power_density(t_surface=temp)
        total_kwh += power_output.value / 1000
        power_output = power_output.value
        dt_power_dict[dt] = power_output

        print(f"{temp}, {power_output}")

    dt_power_df: Final[pd.DataFrame] = pd.DataFrame.from_dict(
        data=dt_power_dict, orient="index", columns=["power"]
    )
    PowerOutputPlot().plot_output_vs_datetime(
        datetimes=dt_power_df.index, power_output=dt_power_df.power
    )

    print(
        f"total kwh between {start_date} and {end_date + timedelta(hours=23)}: {total_kwh} kWh"
    )
