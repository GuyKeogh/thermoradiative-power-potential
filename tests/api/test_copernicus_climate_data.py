from datetime import datetime
from typing import Final

from astropy import units as u


class TestGetValuesFromAPI:
    def test_get_average_monthly_dewpoint_temperature(
        self, surface_temperature_obj_ireland_jan_2022
    ) -> None:
        lat: Final[float] = 53.4
        lon: Final[float] = -6.3
        monthly_average: Final[
            float
        ] = surface_temperature_obj_ireland_jan_2022.get_average_value_from_dataset(
            lat=lat,
            lon=lon,
            dataset_shortname="d2m",
            date=datetime(year=2022, month=1, day=1),
            period="month",
        )
        assert round(monthly_average) == 277

    def test_get_cloud_base_height(self, surface_temperature_obj_ireland_jan_2022):
        lat: Final[float] = 53.4
        lon: Final[float] = -6.3
        value: Final[
            u.Quantity
        ] = surface_temperature_obj_ireland_jan_2022.get_cloud_base_height(
            lat=lat, lon=lon, date=datetime(year=2022, month=1, day=1, hour=1)
        )
        assert round(value.value, 1) == 1244.5
        assert value.unit == u.meter
