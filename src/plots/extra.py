import os
from typing import Final

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from astropy import units as u
from plotly.subplots import make_subplots

from src.calculators.maximum_power_point_tracker import MaximumPowerPointTracker


class ExtraPlots:
    def __init__(self):
        self.base_path: Final[str] = "data/out/extraplots/"
        os.makedirs(self.base_path, exist_ok=True)

        for bandgap in [0.01, 0.10, 0.17]:
            df: pd.DataFrame = self._get_temperatures_vs_power_and_voltage(
                bandgap=bandgap
            )
            self._save_power_and_voltage_vs_temperatures(df=df, bandgap=bandgap)

        df_power_and_voltage_vs_bandgap: Final[
            pd.DataFrame
        ] = self._get_power_and_voltage_vs_bandgap(
            bandgaps=np.arange(start=0.01, stop=1.51, step=0.01), t_surf=300, t_sky=270
        )
        self._bandgap_vs_power_and_voltage(df=df_power_and_voltage_vs_bandgap)

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
            sky_temperatures = range(200, 351)
            surface_temperatures = range(200, 351)

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

    def _get_power_and_voltage_vs_bandgap(
        self, bandgaps: np.ndarray, t_sky: int, t_surf: int
    ):
        csv_filename: Final[str] = f"power_and_voltage_vs_bandgap.csv"
        if os.path.exists(os.path.join(self.base_path, csv_filename)):
            print(f"{csv_filename} exists! Loading...")
            return pd.read_csv(
                os.path.join(self.base_path, csv_filename),
                parse_dates=False,
                index_col=0,
            )
        else:
            t_surf: u.Quantity = t_surf * u.K
            t_sky: u.Quantity = t_sky * u.K

            data_dict: dict[int, tuple[float, int, int, float, float]] = dict()
            index: int = 0
            bg: float
            for bg in bandgaps:
                bandgap: float = round(bg, 2)
                print(f"Trying bandgap: {bandgap}")

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
                    bandgap,
                    t_surf.value,
                    t_sky.value,
                    power_output.value,
                    optimal_voltage.value,
                )
                index += 1

            df: Final[pd.DataFrame] = pd.DataFrame.from_dict(
                data=data_dict,
                columns=[
                    "bandgap",
                    "t_surf",
                    "t_sky",
                    "power_output",
                    "optimum_voltage",
                ],
                orient="index",
            )
            df.to_csv(os.path.join(self.base_path, csv_filename))
            return df

    def _save_power_and_voltage_vs_temperatures(self, df: pd.DataFrame, bandgap: float):
        df_t_sky_270_k: Final[pd.DataFrame] = df.loc[df.t_sky == 270.0]
        df_t_surf_270_k: Final[pd.DataFrame] = df.loc[df.t_surf == 270.0]

        fig = make_subplots(
            rows=2,
            cols=2,
            vertical_spacing=0.15,
            horizontal_spacing=0.1,
            subplot_titles=(
                "Power Density vs Surface Temperature <br>for a Sky Temperature of 270 K",
                "Optimal Voltage vs Surface Temperature<br>for a Sky Temperature of 270 K",
                "Power Density vs Sky Temperature<br>for a Surface Temperature of 270 K",
                "Optimal Voltage vs Sky Temperature<br>for a Surface Temperature of 270 K",
            ),
        )

        fig.add_trace(
            go.Scatter(x=df_t_sky_270_k.t_surf, y=df_t_sky_270_k.power_output),
            row=1,
            col=1,
        )
        fig.add_trace(
            go.Scatter(x=df_t_sky_270_k.t_surf, y=df_t_sky_270_k.optimum_voltage),
            row=1,
            col=2,
        )
        fig.add_trace(
            go.Scatter(x=df_t_surf_270_k.t_sky, y=df_t_surf_270_k.power_output),
            row=2,
            col=1,
        )
        fig.add_trace(
            go.Scatter(x=df_t_surf_270_k.t_sky, y=df_t_surf_270_k.optimum_voltage),
            row=2,
            col=2,
        )

        fig.update_xaxes(title_text="Surface Temperature (K)", row=1, col=1)
        fig.update_yaxes(title_text="Power Density (Wm<sup>-2</sup>)", row=1, col=1)
        fig.update_xaxes(title_text="Surface Temperature (K)", row=1, col=2)
        fig.update_yaxes(title_text="Optimal Voltage (V)", row=1, col=2)
        fig.update_xaxes(title_text="Sky Temperature (K)", row=2, col=1)
        fig.update_yaxes(title_text="Power Density (Wm<sup>-2</sup>)", row=2, col=1)
        fig.update_xaxes(title_text="Sky Temperature (K)", row=2, col=2)
        fig.update_yaxes(title_text="Optimal Voltage (V)", row=2, col=2)

        fig.update_layout(
            width=1000,
            showlegend=False,
            margin=dict(t=150),
            title_text=f"<br>Relationships between Power Density and Optimum Voltage, and Surface and Sky Temperatures, for {bandgap} eV semiconductor</br>",
            title_x=0.5,
        )
        fig.show()

        pio.write_image(
            fig,
            os.path.join(
                self.base_path, f"power_and_voltage_vs_temperatures_{bandgap}eV.svg"
            ),
            format="svg",
        )

    def _bandgap_vs_power_and_voltage(self, df: pd.DataFrame):
        fig = make_subplots(
            rows=1,
            cols=2,
            vertical_spacing=0.15,
            horizontal_spacing=0.15,
            subplot_titles=(
                "Power Density (Wm<sup>-2</sup>) vs Bandgap (eV) for a<br>Sky Temperature of 270 K and Surface Temperature of 300 K",
                "Optimal Voltage (V) vs Bandgap (eV) for a<br>Sky Temperature of 270 K and Surface Temperature of 300 K",
            ),
        )

        fig.add_trace(go.Scatter(x=df.bandgap, y=df.power_output), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.bandgap, y=df.optimum_voltage), row=1, col=2)

        fig.update_xaxes(title_text="Bandgap (eV)", row=1, col=1)
        fig.update_yaxes(title_text="Power Density (Wm<sup>-2</sup>)", row=1, col=1)
        fig.update_xaxes(title_text="Bandgap (eV)", row=1, col=2)
        fig.update_yaxes(title_text="Optimal Voltage (V)", row=1, col=2)

        fig.update_layout(
            width=1000,
            showlegend=False,
            margin=dict(t=175),
            title_text=f"<br>Plots of Power Density and Optimal Voltage, against Semiconductor Bandgaps</br>",
            title_x=0.5,
        )
        fig.show()

        pio.write_image(
            fig,
            os.path.join(self.base_path, f"bandgap_vs_power_and_voltage.svg"),
            format="svg",
        )

    def _save_surface_plot_of_power_vs_temperatures(
        self, df: pd.DataFrame, bandgap: float
    ) -> None:
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

    def _save_surface_plot_of_voltage_vs_temperatures(
        self, df: pd.DataFrame, bandgap: float
    ) -> None:
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
