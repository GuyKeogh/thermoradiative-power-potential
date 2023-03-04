import json
import os
from datetime import datetime
from glob import glob
from typing import Final, Literal

import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

pio.kaleido.scope.mathjax = None


class CreateChoroplethMap:
    def __init__(self):
        pass

    def create_map(
        self, emissivity_method: Literal["swinbank", "cloudy_sky", "martin-berdahl"]
    ) -> None:
        start_date: Final[datetime] = datetime(2023, 1, 1)
        end_date: Final[datetime] = datetime(2023, 1, 31)

        input_dir: Final[str] = os.path.abspath(
            f"data/out/{emissivity_method}/{start_date.strftime('%Y%m%d-%H%M%S')}_{end_date.strftime('%Y%m%d-%H%M%S')}/"
        )
        folderpaths = glob(os.path.join(input_dir, "*"))

        index: int = 0
        data_dict: dict[int, tuple[float, float, float]] = dict()
        for folderpath in folderpaths:
            long_lat_folder_name = os.path.basename(folderpath)
            lat_str, lon_str = long_lat_folder_name.split("_", 1)
            lat: float = float(lat_str)
            lon: float = float(lon_str)

            output_dir: str = os.path.abspath(
                f"data/out/{emissivity_method}/{start_date.strftime('%Y%m%d-%H%M%S')}_{end_date.strftime('%Y%m%d-%H%M%S')}/{lat}_{lon}/"
            )
            filepath: str = os.path.join(output_dir, "json_data.json")
            try:
                with open(filepath, "r") as infile:
                    data = json.load(infile)
                    total_kwh: float = data["total_kwh_per_square_m"]
                    data_dict[index] = (lat, lon, total_kwh)
            except FileNotFoundError:
                print(f"Couldn't find file {filepath}")
                pass
            index += 1

        # df = pd.DataFrame(data=data_dict, columns=["lat", "lon", "value"])
        df: Final[pd.DataFrame] = pd.DataFrame.from_dict(
            data=data_dict, columns=["lat", "lon", "value"], orient="index"
        )
        fig = go.Figure(
            data=go.Scattergeo(
                locationmode="country names",
                lon=df["lon"],
                lat=df["lat"],
                text=df["value"],
                mode="markers",
                marker=dict(
                    color=df["value"],
                    size=8,
                    opacity=0.8,
                    reversescale=True,
                    autocolorscale=False,
                    symbol="square",
                    line=dict(width=1, color="rgba(102, 102, 102)"),
                    colorbar=dict(
                        titleside="right",
                        outlinecolor="rgba(68, 68, 68, 0)",
                        ticks="outside",
                        # showticksuffix="last",
                        # dtick=0.1,
                    ),
                    cmin=0,
                    cmax=df["value"].max(),
                    colorbar_title="Total Power Output (kWh/m<sup>3</sup>)",
                ),
            )
        )

        fig.update_layout(
            # title="Thermoradiative Power Potential by Location (kWh/m<sup>3</sup>) in January 2023 for "
            # f"InSb semiconductor (Eg=0.17eV) with {emissivity_method} sky emissivity determination method",
            geo=dict(
                scope="world",
                showland=True,
                landcolor="rgb(250, 250, 250)",
                subunitcolor="rgb(217, 217, 217)",
                countrycolor="rgb(217, 217, 217)",
                countrywidth=0.5,
                subunitwidth=0.5,
            ),
        )

        fig.show()
        fig.update_layout(
            # autosize=False,
            width=1000,
        )

        pio.write_image(fig, f"assessment_map_{emissivity_method}.png", format="png")
        pio.write_image(fig, f"assessment_map_{emissivity_method}.pdf", format="pdf")
