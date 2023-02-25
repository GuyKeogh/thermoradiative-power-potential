from datetime import datetime, timedelta

from dateutil.rrule import DAILY, rrule


def get_hourly_datetimes_between_period(
    start_date: datetime, end_date: datetime
) -> list[datetime]:
    hourly_datetimes: list[datetime] = []
    for date in rrule(DAILY, dtstart=start_date, until=end_date):
        for hour in range(24):
            hourly_datetimes.append(
                datetime.combine(date, datetime.min.time()) + timedelta(hours=hour)
            )
    return hourly_datetimes
