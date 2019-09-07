import dataset
import urllib.request
import functools
import json
import pandas as pd
from pandas.tseries.offsets import BDay
from pytz import timezone

# IEX time is the START of the period

base_url = "https://cloud.iexapis.com/stable/stock/{}/chart/date/{}?token=pk_61804834a6b84a8d912359e29ca5bd37"

def get_full(symbol, date):
  url = base_url.format(symbol, date)
  print("requesting with {}...".format(url))
  response = urllib.request.urlopen(url).read()
  print("responded")
  parsed_response = json.loads(response.decode('utf-8'))

  from dateutil.parser import parse
  from dateutil.tz import gettz
  timezone = "US/Eastern"
  results = []
  for data in parsed_response:
    t = "{} {} T".format(data['date'], data['minute'])
    ts = int(parse(t, tzinfos={ "T": gettz(timezone) }).timestamp())
    results.append({
      'time': ts,
      'open': data["marketOpen"],
      'high': data["marketHigh"],
      'low': data["marketLow"],
      'close': data["marketClose"],
      'volume': data["marketVolume"]
    })
  print("response size: {}".format(len(results)))
  return results

db = dataset.connect('sqlite:///C:\\Users\\codch\\iex.db')
table_name = 'historical_minutes_ohlcv'

def write_to_db(data_points, symbol):
  table = db[table_name]
  for idx, data_point in enumerate(data_points):
    if (idx % 100 == 0):
      print("writing row {}...".format(idx + 1))
    table.insert_ignore({**data_point, **{'symbol': symbol}}, ['time', 'symbol'])

def get_latest_ts_for_symbol(symbol):
  query = "SELECT MAX(time) FROM {} WHERE symbol = '{}' GROUP BY symbol".format(table_name, symbol)
  res = list(db.query(query))
  if len(res) == 1:
    return pd.Timestamp(list(res[0].values())[0], unit='s', tz='Zulu').tz_convert(timezone('US/Eastern'))
  else:
    return pd.Timestamp("today", tz='Zulu').tz_convert(timezone('US/Eastern')) - BDay(10)

def process(symbol, date=None):
  if date is None:
    date = get_latest_ts_for_symbol(symbol)
    today = pd.Timestamp("today", tz='Zulu').tz_convert(timezone('US/Eastern'))
    while date <= today:
      write_to_db(get_full(symbol, date.to_pydatetime().strftime('%Y%m%d')), symbol)
      date = date + BDay(1)
  else:
    write_to_db(get_full(symbol, date), symbol)

import sys

def main():
  if sys.argv[1] == '-bf':
    symbols = sys.argv[3:]
  else:
    symbols = sys.argv[1:]

  for symbol in symbols:
    if sys.argv[1] == '-bf':
      process(symbol, sys.argv[2])
    else:
      process(symbol)

if __name__ == "__main__":
  main()
