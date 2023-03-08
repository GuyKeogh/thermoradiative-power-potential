import json
import os
from datetime import datetime
from glob import glob
from typing import Final, Literal

import pandas as pd


def get_dict_of_processed_data(
    emissivity_method: Literal["swinbank", "martin-berdahl"],
    start_date: datetime,
    end_date: datetime,
) -> dict[int, tuple[float, float, float, pd.DataFrame]]:
    input_dir: Final[str] = os.path.abspath(
        f"data/out/{emissivity_method}/{start_date.strftime('%Y%m%d-%H%M%S')}_{end_date.strftime('%Y%m%d-%H%M%S')}/"
    )
    folderpaths = glob(os.path.join(input_dir, "*"))

    index: int = 0
    data_dict: dict[int, tuple[float, float, float, pd.DataFrame]] = dict()
    for folderpath in folderpaths:
        long_lat_folder_name = os.path.basename(folderpath)
        lat_str, lon_str = long_lat_folder_name.split("_", 1)
        lat: float = float(lat_str)
        lon: float = float(lon_str)

        output_dir: str = os.path.abspath(
            f"data/out/{emissivity_method}/{start_date.strftime('%Y%m%d-%H%M%S')}_{end_date.strftime('%Y%m%d-%H%M%S')}/"
            f"{lat}_{lon}/"
        )
        json_filepath: str = os.path.join(output_dir, "json_data.json")
        df_filepath: str = os.path.join(output_dir, "data_per_dt.csv")
        try:
            df: pd.DataFrame = pd.read_csv(
                filepath_or_buffer=df_filepath, index_col=0, parse_dates=True
            )
            with open(json_filepath, "r") as infile:
                data = json.load(infile)
                total_kwh: float = data["total_kwh_per_square_m"]
                data_dict[index] = (lat, lon, total_kwh, df)

        except FileNotFoundError:
            print(f"Couldn't find file {json_filepath}")
            pass
        index += 1

    return data_dict
