import argparse
from datetime import datetime
from typing import Final

from src.plots.resource_assessment_choropleth_map import CreateChoroplethMap
from src.processing.process_power_output import (
    get_test_power_output_for_set_temperatures,
    process_batch,
)

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
    "--skip_predict",
    help="If passed, the application will not process potential power output at locations"
    "Example usage: `python main.py --skip_predict`",
    action="store_true",
    required=False,
)
args = parser.parse_args()


if __name__ == "__main__":
    if not args.skip_predict:
        start_date: Final[datetime] = datetime(2023, 1, 1)
        end_date: Final[datetime] = datetime(2023, 1, 31)

        if args.batch_start is None:
            print(
                "Running in demonstration mode. Pass --batch_start to process real data."
            )
            get_test_power_output_for_set_temperatures()
        else:
            print(f"Processing from {args.batch_start}")
            process_batch(
                batch_start=args.batch_start,
                batch_quantity=None,
                start_date=start_date,
                end_date=end_date,
            )

    if not args.skip_worldmap:
        CreateChoroplethMap().create_map()
