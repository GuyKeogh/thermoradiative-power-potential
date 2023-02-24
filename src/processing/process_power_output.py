from datetime import datetime
from typing import Final

from astropy import units as u

from src.api.copernicus_climate_data import CopernicusClimateData
from src.calculators.coordinates_for_assessment import get_coordinates_for_assessment
from src.calculators.maximum_power_point_tracker import MaximumPowerPointTracker
from src.processing.save_output_between_dates import save_power_output_between_dates


def get_test_power_output() -> u.Quantity:
    t_surf = 300 * u.Kelvin
    t_sky = 270 * u.Kelvin
    semiconductor_bandgap: Final[u.Quantity] = 0.1 * u.electronvolt

    power_output = MaximumPowerPointTracker(
        t_cell=t_surf, t_sky=t_sky, E_g=semiconductor_bandgap
    ).get_max_power()
    print(
        f"Surface temperature = {t_surf} and sky temperature = {t_sky}.\nPower output = {power_output.value}W"
    )
    return power_output


def process_batch(
    climate_data_obj: CopernicusClimateData,
    start_date: datetime,
    end_date: datetime,
    batch_start: int,
    batch_quantity: int,
) -> None:
    batch_start_plus_quantity: Final[int] = batch_start + batch_quantity

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
            climate_data_obj=climate_data_obj,
            lon=lon,
            lat=lat,
            start_date=start_date,
            end_date=end_date,
        )
