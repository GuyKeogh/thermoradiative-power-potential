import json
import os
from datetime import datetime

# df = pd.DataFrame(data=[[53.5, -6.5, 400]], columns=["lat", "lon", "value"])
from glob import glob
from typing import Final

import pandas as pd
import plotly.graph_objects as go


class CreateChoroplethMap:
    def __init__(self):
        pass

    def create_map(self) -> None:
        start_date: Final[datetime] = datetime(2023, 1, 1)
        end_date: Final[datetime] = datetime(2023, 1, 31)

        input_dir: Final[str] = os.path.abspath(
            f"data/out/{start_date.strftime('%Y%m%d-%H%M%S')}_{end_date.strftime('%Y%m%d-%H%M%S')}/"
        )
        folderpaths = glob(os.path.join(input_dir, "*"))

        index: int = 0
        data_dict: dict[int, list[float, float, float]] = dict()
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
                    colorbar_title="Power Output (kWh)",
                ),
            )
        )

        fig.update_layout(
            title="Potential Power Output by Location (kWh) in January 2023 for InSb semiconductor (Eg=0.17eV)",
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

        """
        
        def create_feature_dict(lon: float, lat: float) -> dict:
            lon_start = math.floor(lon)
            lon_end = math.ceil(lon)
            lat_start = math.floor(lat)
            lat_end = math.ceil(lat)
            return {"type": "Feature",
                    "id": 1,
                    "geometry": {"type": "Polygon", "coordinates": [[lon_start, lat_start], [lon_end, lat_start], [lon_start, lat_end], [lon_end, lat_end]]}}
        
        counties = {
            "type": "FeatureCollection",
            "features": [create_feature_dict(lon=-6.5, lat=53.5), create_feature_dict(lon=1.5, lat=3.5)]
        }
        
        fig = px.choropleth(df, geojson=counties, locations='fips', color='value',
                                   color_continuous_scale="Viridis",
                                   range_color=(0, 500),
                                   scope="world",
                                   labels={'unemp':'unemployment rate'},
                                   projection="EPSG3857"
                                  )
        
        fig.show()
        
        import pandas as pd
        df = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/fips-unemp-16.csv",
                           dtype={"fips": str})
        
        import plotly.express as px
        
        fig = px.choropleth(df, geojson=counties, locations='fips', color='unemp',
                                   color_continuous_scale="Viridis",
                           range_color=(0, 12),
                           scope="usa",
                           labels={'unemp':'unemployment rate'}
                          )
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.show()
"""
