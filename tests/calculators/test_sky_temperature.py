from datetime import datetime

from astropy import units as u

from src.api.copernicus_climate_data import CopernicusClimateData
from src.calculators.sky_temperature import SkyTemperature


class TestCalculateSkyTemperature:
    def test_martin_berdahl_method(
        self, surface_temperature_obj_ireland_jan_2022: CopernicusClimateData
    ):
        lat: float = 53.4
        lon: float = -6.3
        t_sky: u.Quantity = SkyTemperature(
            surface_temperature_obj=surface_temperature_obj_ireland_jan_2022,
            lat=lat,
            lon=lon,
        ).get_sky_temperature(
            date=datetime(year=2022, month=1, day=1, hour=3), formula="martin-berdahl"
        )
        assert round(t_sky.value, 2) == 282.72
        assert t_sky.unit == u.Kelvin
