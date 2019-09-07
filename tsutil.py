from datetime import datetime
import pytz
from dateutil.parser import parse

def string_to_timestamp(datetime_str):
  # datetime_str is interpreted as eastern time
  return int(datetime.timestamp(pytz.timezone('US/Eastern').localize(parse(datetime_str))))

def timestamp_to_string(timestamp):
  return datetime.fromtimestamp(timestamp, tz=pytz.timezone('US/Eastern')).strftime("%Y-%m-%d")