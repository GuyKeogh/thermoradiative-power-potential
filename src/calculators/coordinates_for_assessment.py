import itertools
from typing import Final

import numpy as np
from global_land_mask import globe


def get_coordinates_for_assessment() -> list[tuple[float, float]]:
    """EPSG3857"""

    """
    for folderpath in folderpaths:
        long_lat_folder_name = os.path.basename(folderpath)
        lat, lon = long_lat_folder_name.split("_", 1)

        output_dir: str = os.path.abspath(
            f"data/out/{start_date.strftime('%Y%m%d-%H%M%S')}_{end_date.strftime('%Y%m%d-%H%M%S')}/{lat}_{lon}/"
        )
        filepath: str = os.path.join(output_dir, "json_data.json")
        try:
            with open(filepath, "r") as infile:
                data = json.load(infile)
                total_kwh: float = data["total_kwh_per_square_m"]
                data_dict[index] = [lat, lon, total_kwh]
        except FileNotFoundError:
            print(f"Couldn't find file {filepath}")
            pass
        index += 1
    """

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
