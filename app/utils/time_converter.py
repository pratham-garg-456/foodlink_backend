from datetime import datetime
import pytz
import tzlocal


def convert_string_time_to_iso(date_time, time_str):
    # Combine the date and the time
    datetime_str = f"{date_time} {time_str}"

    # Parse the datetime str into a datetime obj
    datetime_obj = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")

    # Localize the naive datetime to local time
    local_tz = pytz.timezone(tzlocal.get_localzone_name())

    toronto_datetime = local_tz.localize(datetime_obj)

    # Convert local time to UTC
    utc_datetime = toronto_datetime.astimezone(pytz.utc)

    # Convert to ISO format to store in db
    iso_time = utc_datetime.isoformat()

    return iso_time
