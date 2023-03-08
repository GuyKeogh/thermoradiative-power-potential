import os
from datetime import datetime
from typing import Final, Literal

import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots

from src.plots.processed_data_loader import get_dict_of_processed_data

pio.kaleido.scope.mathjax = None


class CreateTemperaturePlots:
    def plot_temperatures_and_power_vs_dates(
        self, emissivity_method: Literal["swinbank", "martin-berdahl"]
    ) -> None:
        start_date: Final[datetime] = datetime(2022, 1, 1)
        end_date: Final[datetime] = datetime(2022, 12, 31)

        data_dict: Final[
            dict[int, tuple[float, float, float, pd.DataFrame]]
        ] = get_dict_of_processed_data(
            emissivity_method=emissivity_method,
            start_date=start_date,
            end_date=end_date,
        )
        for key, value in data_dict.items():
            lat, lon, total_kwh, df = value
            self._create_plot(
                lat=lat, lon=lon, emissivity_method=emissivity_method, df=df
            )

    @staticmethod
    def _create_plot(
        lat: float, lon: float, emissivity_method: str, df: pd.DataFrame
    ) -> None:
        fig = make_subplots(
            rows=2,
            cols=1,
            start_cell="bottom-left",
            shared_xaxes=True,
            vertical_spacing=0.02,
        )

        fig.add_trace(
            go.Scatter(x=df.index, y=df.t_sky, name="Sky Temperature"), row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=df.index, y=df.t_surf, name="Surface Temperature"),
            row=1,
            col=1,
        )
        fig.update_xaxes(title_text="Date", row=1, col=1)
        fig.update_yaxes(title_text="Temperature (K)", row=1, col=1)

        fig.add_trace(
            go.Scatter(
                x=df.index, y=df.average_power_watts_per_sqm, name="Average Power"
            ),
            row=2,
            col=1,
        )
        fig.update_yaxes(
            title_text="Average Power Potential (Wm<sup>-2</sup>)", row=2, col=1
        )

        fig.show()

        fig.update_layout(
            width=1000,
        )

        base_path: Final[str] = f"data/out/plots/{emissivity_method}/{lat}_{lon}/"
        os.makedirs(base_path, exist_ok=True)
        pio.write_image(
            fig,
            os.path.join(
                base_path, f"power_and_temperatures_vs_time_{emissivity_method}.pdf"
            ),
            format="pdf",
        )
