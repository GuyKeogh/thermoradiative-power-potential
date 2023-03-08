import os
from typing import Final

import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from astropy import units as u

from src.calculators.maximum_power_point_tracker import MaximumPowerPointTracker


class ExtraPlots:
    def __init__(self):
        self.base_path: Final[str] = "data/out/extraplots/"
        os.makedirs(self.base_path, exist_ok=True)

        for bandgap in [0.01, 0.10, 0.17]:
            df: pd.DataFrame = self._get_temperatures_vs_power_and_voltage(
                bandgap=bandgap
            )
            self._save_power_vs_temperatures(df=df, bandgap=bandgap)
            self._save_voltage_vs_temperatures(df=df, bandgap=bandgap)

    def _get_temperatures_vs_power_and_voltage(self, bandgap: float):
        csv_filename: Final[str] = f"power_voltage_per_temp_{bandgap}eV.csv"
        if os.path.exists(os.path.join(self.base_path, csv_filename)):
            print(f"{csv_filename} exists! Loading...")
            return pd.read_csv(
                os.path.join(self.base_path, csv_filename),
                parse_dates=False,
                index_col=0,
            )
        else:
            sky_temperatures = range(200, 350)
            surface_temperatures = range(200, 350)

            data_dict: dict[int, tuple[int, int, float, float]] = dict()
            index: int = 0
            for sky_temp, surf_temp in [
                (sky_temp, surf_temp)
                for sky_temp in sky_temperatures
                for surf_temp in surface_temperatures
            ]:
                print(f"Trying sky_temp: {sky_temp}, surface_temp: {surf_temp}")
                t_surf: u.Quantity = surf_temp * u.K
                t_sky: u.Quantity = sky_temp * u.K

                mpp_object = MaximumPowerPointTracker(
                    E_g=bandgap * u.eV,
                    t_sky=t_sky,
                    t_cell=t_surf,
                )
                power_output = mpp_object.max_power
                optimal_voltage = mpp_object.optimal_voltage
                print(
                    f"Produced {power_output} at optimal voltage of {mpp_object.optimal_voltage}"
                )
                data_dict[index] = (
                    t_surf.value,
                    t_sky.value,
                    power_output.value,
                    optimal_voltage.value,
                )
                index += 1

            df: Final[pd.DataFrame] = pd.DataFrame.from_dict(
                data=data_dict,
                columns=["t_surf", "t_sky", "power_output", "optimum_voltage"],
                orient="index",
            )
            df.to_csv(os.path.join(self.base_path, csv_filename))

            return df

    def _save_power_vs_temperatures(self, df: pd.DataFrame, bandgap: float) -> None:
        power_df: Final[pd.DataFrame] = df.set_index(["t_surf", "t_sky"])[
            "power_output"
        ].unstack()

        fig = go.Figure(
            data=[go.Surface(x=power_df.index, y=power_df.columns, z=power_df.values)]
        )

        fig.update_layout(
            scene=dict(
                xaxis_title="Sky Temperature (K)",
                yaxis_title="Surface Temperature (K)",
                zaxis_title="Power Output (Wm<sup>-2</sup>)",
                xaxis=dict(
                    nticks=4,
                    range=[df.t_sky.min(), df.t_sky.max()],
                ),
                yaxis=dict(
                    nticks=4,
                    range=[df.t_surf.min(), df.t_surf.max()],
                ),
            ),
        )
        fig.show()
        pio.write_image(
            fig,
            os.path.join(self.base_path, f"power_per_temp_{bandgap}eV.pdf"),
            format="pdf",
        )
        fig.write_html(os.path.join(self.base_path, f"power_per_temp_{bandgap}eV.html"))

    def _save_voltage_vs_temperatures(self, df: pd.DataFrame, bandgap: float) -> None:
        voltage_df: Final[pd.DataFrame] = df.set_index(["t_surf", "t_sky"])[
            "optimum_voltage"
        ].unstack()

        fig = go.Figure(
            data=[
                go.Surface(
                    x=voltage_df.index, y=voltage_df.columns, z=voltage_df.values
                )
            ]
        )

        fig.update_layout(
            scene=dict(
                xaxis_title="Sky Temperature (K)",
                yaxis_title="Surface Temperature (K)",
                zaxis_title="Optimum Voltage (V)",
                xaxis=dict(
                    nticks=4,
                    range=[df.t_sky.min(), df.t_sky.max()],
                ),
                yaxis=dict(
                    nticks=4,
                    range=[df.t_surf.min(), df.t_surf.max()],
                ),
            ),
        )
        fig.show()
        pio.write_image(
            fig,
            os.path.join(self.base_path, f"voltage_per_temp_{bandgap}eV.pdf"),
            format="pdf",
        )
        fig.write_html(
            os.path.join(self.base_path, f"voltage_per_temp_{bandgap}eV.html")
        )
