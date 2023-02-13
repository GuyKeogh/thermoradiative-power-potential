import pandas as pd
import plotly.express as px


class PowerOutputPlot:
    def __init__(self):
        pass

    def plot_output_vs_datetime(
        self, power_output: pd.Series, datetimes: pd.Series
    ) -> None:
        fig = px.line(
            y=power_output,
            x=datetimes,
            title="Power Output vs. Datetime",
            labels={"x": "Datetime", "y": "Average Power Output (W)"},
            color_discrete_sequence=["black"],
        )
        fig.show()
