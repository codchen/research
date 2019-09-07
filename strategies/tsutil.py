from datetime import datetime, date
import pytz
from dateutil.parser import parse

def string_to_timestamp(datetime_str):
  # datetime_str is interpreted as eastern time
  return int(datetime.timestamp(pytz.timezone('US/Eastern').localize(parse(datetime_str))))

def string_to_date(date_str):
  return parse(date_str).date()

def timestamp_to_string(timestamp):
  return timestamp_to_datetime(timestamp).strftime("%Y-%m-%d")

def timestamp_to_datetime(timestamp):
  return datetime.fromtimestamp(timestamp, tz=pytz.timezone('US/Eastern'))

def timestamp_to_date(timestamp):
  return date.fromtimestamp(timestamp)