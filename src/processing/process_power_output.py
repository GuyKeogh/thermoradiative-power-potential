import warnings
from datetime import datetime
from typing import Final, Literal

from astropy import units as u

from src.api.copernicus_climate_data import CopernicusClimateData
from src.calculators.coordinates_for_assessment import get_coordinates_for_assessment
from src.calculators.maximum_power_point_tracker import MaximumPowerPointTracker
from src.exceptions import InsufficientClimateDataError
from src.processing.save_output_between_dates import save_power_output_between_dates


def get_test_power_output_for_set_temperatures() -> u.Quantity:
    t_surf = 300 * u.Kelvin
    t_sky = 270 * u.Kelvin
    semiconductor_bandgap: Final[u.Quantity] = 0.17 * u.electronvolt

    power_output = MaximumPowerPointTracker(
        t_cell=t_surf, t_sky=t_sky, E_g=semiconductor_bandgap
    ).get_max_power()
    print(
        f"Surface temperature = {t_surf} and sky temperature = {t_sky}.\nPower output = {power_output.value}W"
    )
    return power_output


def save_test_power_output_for_set_lon_lat() -> None:
    start_date: Final[datetime] = datetime(2022, 1, 1)
    end_date: Final[datetime] = datetime(2022, 12, 31)
    lat: Final[float] = 53.4
    lon: Final[float] = -6.3

    climate_data_obj: Final[CopernicusClimateData] = CopernicusClimateData(
        if_load_entire_earth=False,
        lat=lat,
        lon=lon,
        year=start_date.year,
        months=[*range(start_date.month, end_date.month + 1)],
    )
    save_power_output_between_dates(
        climate_data_obj=climate_data_obj,
        lon=lon,
        lat=lat,
        start_date=start_date,
        end_date=end_date,
        emissivity_method="martin-berdahl",
    )


def process_batch(
    start_date: datetime,
    end_date: datetime,
    batch_start: int,
    batch_quantity: int | None,
    emissivity_method: Literal["swinbank", "cloudy_sky", "martin-berdahl"],
) -> None:
    coordinates_for_assessment: Final[
        list[tuple[float, float]]
    ] = get_coordinates_for_assessment()

    if batch_quantity is None:
        batch_end = len(coordinates_for_assessment)
    else:
        batch_start_plus_quantity: Final[int] = batch_start + batch_quantity

        batch_end = (
            batch_start_plus_quantity
            if batch_start_plus_quantity <= len(coordinates_for_assessment)
            else len(coordinates_for_assessment)
        )
    for lon, lat in coordinates_for_assessment[batch_start:batch_end]:
        print(f"Processing co-ordinate lon:{lon}, lat:{lat}")
        climate_data_obj: CopernicusClimateData = CopernicusClimateData(
            if_load_entire_earth=False,
            lon=lon,
            lat=lat,
            year=start_date.year,
            months=[*range(start_date.month, end_date.month + 1)],
        )

        try:
            save_power_output_between_dates(
                climate_data_obj=climate_data_obj,
                lon=lon,
                lat=lat,
                start_date=start_date,
                end_date=end_date,
                emissivity_method=emissivity_method,
            )
        except InsufficientClimateDataError as e:
            warnings.warn(f"{e}. Skipping lat: {lat}, lon: {lon}.")
