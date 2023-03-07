import os
from datetime import datetime
from typing import Final, Literal

import pandas as pd
import plotly.express as px
import plotly.io as pio

from src.plots.processed_data_loader import get_dict_of_processed_data


class SummaryStatistics:
    def output_summary_statistics(
        self, emissivity_method: Literal["swinbank", "martin-berdahl"]
    ):
        start_date: Final[datetime] = datetime(2022, 1, 1)
        end_date: Final[datetime] = datetime(2022, 12, 31)
        data_dict: Final[
            dict[int, tuple[float, float, float, pd.DataFrame]]
        ] = get_dict_of_processed_data(
            emissivity_method=emissivity_method,
            start_date=start_date,
            end_date=end_date,
        )

        for index, data_tuple in data_dict.items():
            lat, lon, total_kwh, df = data_tuple
            df = df[df["average_power_watts_per_sqm"] >= 0]

            base_path: str = f"data/out/plots/{emissivity_method}/{lat}_{lon}/"
            os.makedirs(base_path, exist_ok=True)

            hour_means: pd.Series = df.groupby(df.index.hour)[
                "average_power_watts_per_sqm"
            ].mean()

            month_means: pd.Series = df.groupby(df.index.month)[
                "average_power_watts_per_sqm"
            ].mean()
            month_means.index = [
                "January",
                "February",
                "March",
                "April",
                "May",
                "June",
                "July",
                "August",
                "September",
                "October",
                "November",
                "December",
            ]
            # month_means.index = month_means.index.map(lambda x: x.month_name())

            output_dir: str = os.path.abspath(
                f"data/out/{emissivity_method}/{start_date.strftime('%Y%m%d-%H%M%S')}_{end_date.strftime('%Y%m%d-%H%M%S')}/{lat}_{lon}/"
            )
            hour_means.to_csv(os.path.join(output_dir, "mean_by_hour.csv"))
            month_means.to_csv(os.path.join(output_dir, "mean_by_month.csv"))
            fig = px.bar(
                hour_means,
                labels={
                    "value": "Mean Potential Power (Wm<sup>-2</sup>)",
                    "index": "Hour of Day",
                },
            )
            fig_month = px.bar(
                month_means,
                labels={
                    "value": "Mean Potential Power (Wm<sup>-2</sup>)",
                    "index": "Month of Year",
                },
            )
            fig.show()
            fig_month.show()

            pio.write_image(
                fig,
                os.path.join(
                    base_path, f"mean_potential_by_hour_{emissivity_method}.pdf"
                ),
                format="pdf",
            )
            pio.write_image(
                fig_month,
                os.path.join(
                    base_path, f"mean_potential_by_month_{emissivity_method}.pdf"
                ),
                format="pdf",
            )
