from datetime import datetime
from typing import Final

import pytest

from src.api.copernicus_climate_data import CopernicusClimateData


@pytest.fixture
def surface_temperature_obj_ireland_jan_2022() -> CopernicusClimateData:
    lat: Final[float] = 53.4
    lon: Final[float] = -6.3

    start_date: Final[datetime] = datetime(2022, 1, 1)
    end_date: Final[datetime] = datetime(2022, 1, 31)
    return CopernicusClimateData(
        lon=lon,
        lat=lat,
        year=start_date.year,
        months=[*range(start_date.month, end_date.month + 1)],
    )
