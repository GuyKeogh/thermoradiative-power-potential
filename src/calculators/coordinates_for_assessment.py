import itertools
from typing import Final

import numpy as np
from global_land_mask import globe


def get_coordinates_for_assessment() -> list[tuple[float, float]]:
    """EPSG3857"""
    lats: Final[np.ndarray] = np.arange(start=-84.5, stop=84.5, step=5)
    lons: Final[np.ndarray] = np.arange(start=-179.5, stop=179.5, step=5)

    lon: float
    lat: float
    coords_to_assess: list[tuple[float, float]] = list()
    for lon, lat in itertools.product(lons, lats):
        if globe.is_land(lat=lat, lon=lon):
            coords_to_assess.append((lon, lat))
    print(f"{len(coords_to_assess)} coordinates to assess")

    return coords_to_assess
