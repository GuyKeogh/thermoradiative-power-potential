import argparse
from datetime import datetime
from typing import Final, Literal

from src.plots.extra import ExtraPlots
from src.plots.resource_assessment_choropleth_map import CreateChoroplethMap
from src.plots.temperature_plot import CreateTemperaturePlots
from src.processing.process_power_output import (
    process_batch,
    save_test_power_output_for_set_lon_lat,
)
from src.stats.summary_statistics import SummaryStatistics

parser = argparse.ArgumentParser(prog="Thermoradiative Power Output Prediction")
parser.add_argument(
    "--batch_start",
    help="Where to start at within coordinates for processing, for batched processing",
    type=int,
    required=False,
)
parser.add_argument(
    "--skip_worldmap",
    help="If passed, the application will not create worldmap with saved datapoints overlaid. "
    "Example usage: `python main.py --skip_worldmap`",
    action="store_true",
    required=False,
)
parser.add_argument(
    "--skip_tempplot",
    help="If passed, the application will not create plots of powers for surface vs sky temperatures by date. "
    "Example usage: `python main.py --skip_tempplot`",
    action="store_true",
    required=False,
)
parser.add_argument(
    "--skip_predict",
    help="If passed, the application will not process potential power output at locations"
    "Example usage: `python main.py --skip_predict`",
    action="store_true",
    required=False,
)
parser.add_argument(
    "--skip_summarystatistics",
    help="If passed, the application will not process summary statistics at locations"
    "Example usage: `python main.py --skip_summarystatistics`",
    action="store_true",
    required=False,
)
parser.add_argument(
    "--skip_extraplots",
    help="If passed, the application will not create generic plots to show relationships"
    "Example usage: `python main.py --skip_extraplots`",
    action="store_true",
    required=False,
)
parser.add_argument(
    "--emissivity_method",
    help="If passed, sets what method to use to calculate emissivity."
    "Example usage: `python main.py --emissivity_method martin-berdahl`",
    choices=["swinbank", "martin-berdahl"],
    nargs=1,
    default=["martin-berdahl"],
)
args = parser.parse_args()


if __name__ == "__main__":
    allowed_emissivity_methods = {"swinbank", "martin-berdahl"}
    emissivity_method: Final[
        Literal["swinbank", "martin-berdahl"]
    ] = args.emissivity_method[0]
    if emissivity_method not in allowed_emissivity_methods:
        raise ValueError("Emissivity method not allowed", emissivity_method)

    if not args.skip_predict:
        start_date: Final[datetime] = datetime(2023, 1, 1)
        end_date: Final[datetime] = datetime(2023, 1, 31)

        if args.batch_start is None:
            print(
                "Running in demonstration mode. Pass --batch_start to process real data."
            )
            save_test_power_output_for_set_lon_lat(emissivity_method=emissivity_method)

        else:
            print(f"Processing from {args.batch_start}")
            process_batch(
                batch_start=args.batch_start,
                batch_quantity=None,
                start_date=start_date,
                end_date=end_date,
                emissivity_method=emissivity_method,
            )

    if not args.skip_worldmap:
        CreateChoroplethMap().create_map(emissivity_method=emissivity_method)

    if not args.skip_tempplot:
        CreateTemperaturePlots().plot_temperatures_and_power_vs_dates(
            emissivity_method=emissivity_method
        )

    if not args.skip_summarystatistics:
        SummaryStatistics().output_summary_statistics(
            emissivity_method=emissivity_method
        )

    if not args.skip_extraplots:
        ExtraPlots()
