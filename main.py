from datetime import datetime, timedelta
from typing import Final

import pandas as pd

# from src.calculators.electric_potential import get_semiconductor_electric_potential
from astropy import constants as const
from astropy import units as u

from src.api.copernicus_climate_data import CopernicusClimateData
from src.calculators.sky_temperature import SkyTemperature
from src.calculators.total_power_output import TotalPowerOutput
from src.constants import Characteristics_HgCdZnTe
from src.dates import get_hourly_datetimes_between_period
from src.plots.power_output import PowerOutputPlot


def get_test_power_output():
    t_surf = 443 * u.Kelvin
    t_sky = 270 * u.Kelvin

    voltage = -0.05 * u.volt
    chemical_potential_driving_emission = (
        voltage.value * u.eV
    )  # https://doi.org/10.1039/D2NR02652J

    power_output = TotalPowerOutput(E_g=0.1 * u.electronvolt).get_total_power_output(
        voltage=voltage,
        t_sky=t_sky,
        t_cell=t_surf,
        chemical_potential_driving_emission=chemical_potential_driving_emission,
    )

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

    total_kwh: float = 0.0
    for dt in get_hourly_datetimes_between_period(
        start_date=start_date, end_date=end_date
    ):
        t_surf: u.Quantity = surface_temperature_obj.get_surface_temperature(date=dt)
        t_sky: u.Quantity = SkyTemperature(
            surface_temperature_obj=surface_temperature_obj
        ).get_sky_temperature(date=dt, formula="martin-berdahl")

        voltage: u.Quantity = -0.1 * u.volt
        chemical_potential_driving_emission: u.Quantity = voltage.value * u.eV

        power_output = TotalPowerOutput(
            E_g=0.1 * u.electronvolt
        ).get_total_power_output(
            voltage=voltage,
            t_sky=t_sky,
            t_cell=t_surf,
            chemical_potential_driving_emission=chemical_potential_driving_emission,
        )

        total_kwh += power_output.value / 1000
        power_output = power_output.value
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

    """
    lat: Final[float] = 53.4
    lon: Final[float] = -6.3

    start_date: Final[datetime] = datetime(year=2022, month=1, day=1)
    end_date: Final[datetime] = datetime(year=2022, month=1, day=31)
    surface_temperature_obj_ireland_jan_2022 = CopernicusClimateData(
        lon=lon,
        lat=lat,
        year=start_date.year,
        months=[*range(start_date.month, end_date.month + 1)],
    )

    t_sky: u.Quantity = SkyTemperature(
        surface_temperature_obj=surface_temperature_obj_ireland_jan_2022
    ).get_sky_temperature(
        date=datetime(year=2022, month=1, day=1, hour=3), formula="martin-berdahl"
    )
    print(t_sky)
    """
