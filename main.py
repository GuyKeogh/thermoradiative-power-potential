import time
from datetime import datetime, timedelta
from typing import Final

import xarray as xr
from astropy import units as u
from dateutil.rrule import DAILY, rrule

from src.calculators.total_power_output import TotalPowerOutput
from src.constants import Characteristics_HgCdZnTe
from src.surface_temperature.surface_temperature_api import SurfaceTemperature

if __name__ == "__main__":
    lat = 53.3608909
    lon = -6.3061867

    start_date: Final[datetime] = datetime(2022, 1, 1)
    end_date: Final[datetime] = datetime(2022, 1, 31)
    surface_temperature_obj: Final[SurfaceTemperature] = SurfaceTemperature(
        lon=lon, lat=lat, year=start_date.year, month=start_date.month
    )

    dt_power_dict: dict[datetime, u.Quantity] = dict()

    for date in rrule(DAILY, dtstart=start_date, until=end_date):
        for hour in range(24):
            dt: datetime = datetime.combine(date, datetime.min.time()) + timedelta(
                hours=hour
            )
            temp: float = surface_temperature_obj.get_temperature(
                lon=lon, lat=lat, date=dt
            )

            power_output = TotalPowerOutput(
                E_g=0.01 * u.electronvolt
            ).get_extractible_power_density(t_surface=temp * u.Kelvin)
            power_output = power_output.value * u.watt
            dt_power_dict[dt] = power_output

            print(f"{temp}, {power_output}")
