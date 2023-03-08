import os
from datetime import datetime
from typing import Final, Literal

import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

from src.plots.processed_data_loader import get_dict_of_processed_data

pio.kaleido.scope.mathjax = None


class CreateChoroplethMap:
    def create_map(
        self, emissivity_method: Literal["swinbank", "martin-berdahl"]
    ) -> None:
        start_date: Final[datetime] = datetime(2023, 1, 1)
        end_date: Final[datetime] = datetime(2023, 1, 31)
        data_dict: Final[
            dict[int, tuple[float, float, float, pd.DataFrame]]
        ] = get_dict_of_processed_data(
            emissivity_method=emissivity_method,
            start_date=start_date,
            end_date=end_date,
        )

        df: Final[pd.DataFrame] = pd.DataFrame.from_dict(
            data=data_dict,
            columns=["lat", "lon", "value", "average_power_watts_per_sqm"],
            orient="index",
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
                    colorbar_title="Total Power Output (kWh/m<sup>2</sup>)",
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
            width=1000,
        )

        base_path: Final[str] = f"data/out/plots/{emissivity_method}/"
        os.makedirs(base_path, exist_ok=True)
        pio.write_image(
            fig,
            os.path.join(base_path, f"assessment_map_{emissivity_method}.pdf"),
            format="pdf",
        )
