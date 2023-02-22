from datetime import datetime
from typing import Final

from astropy import units as u

from src.api.copernicus_climate_data import CopernicusClimateData
from src.calculators.sky_temperature import SkyTemperature


class TestGetValuesFromAPI:
    def test_get_average_monthly_dewpoint_temperature(
        self, surface_temperature_obj_ireland_jan_2022
    ) -> None:
        monthly_average: Final[
            float
        ] = surface_temperature_obj_ireland_jan_2022.get_average_value_from_dataset(
            dataset_shortname="d2m",
            date=datetime(year=2022, month=1, day=1),
            period="month",
        )
        assert round(monthly_average) == 277

    def test_get_cloud_base_height(self, surface_temperature_obj_ireland_jan_2022):
        value: Final[
            u.Quantity
        ] = surface_temperature_obj_ireland_jan_2022.get_cloud_base_height(
            date=datetime(year=2022, month=1, day=1, hour=1)
        )
        assert value == 8.0 * u.meter
