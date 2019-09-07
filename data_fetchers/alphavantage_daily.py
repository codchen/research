import dataset
import urllib.request
import functools
import json

# Alphavantage time is the END time of the period

base_url = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&outputsize=full&apikey=GEGM4SX2DR9VJB68"
base_adjusted_url = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&outputsize=full&apikey=GEGM4SX2DR9VJB68"

def get_full(symbol, adjusted=False):
  url = (base_adjusted_url if adjusted else base_url) + "&symbol={}".format(symbol)
  print("requesting with {}...".format(url))
  response = urllib.request.urlopen(url).read()
  print("responded")
  parsed_response = json.loads(response.decode('utf-8'))

  from dateutil.parser import parse
  from dateutil.tz import gettz
  timezone = parsed_response["Meta Data"]["5. Time Zone"]
  results = []
  for t, p in parsed_response["Time Series (Daily)"].items():
    t = "{} 17:00:00 T".format(t)
    ts = int(parse(t, tzinfos={ "T": gettz(timezone) }).timestamp())
    ratio = float(p['5. adjusted close']) / float(p['4. close']) if adjusted else 1
    results.append({
      'time': ts,
      'open': float(p["1. open"]) * ratio,
      'high': float(p["2. high"]) * ratio,
      'low': float(p["3. low"]) * ratio,
      'close': float(p['5. adjusted close']) if adjusted else float(p['4. close']),
      'volume': p["6. volume"] if adjusted else p['5. volume']
    })
  print("response size: {}".format(len(results)))
  return results

db = dataset.connect('sqlite:///C:\\Users\\codch\\alphavantage.db')
table_name = 'historical_daily_ohlcv'
table_name_adjusted = 'historical_daily_adjusted_ohlcv'

def write_to_db(data_points, symbol, adjusted=False):
  table = db[table_name_adjusted if adjusted else table_name]
  for idx, data_point in enumerate(data_points):
    if (idx % 100 == 0):
      print("writing row {}...".format(idx + 1))
    table.insert_ignore({**data_point, **{'symbol': symbol}}, ['time', 'symbol'])

def process(symbol, adjusted=False):
  write_to_db(get_full(symbol, adjusted), symbol, adjusted)

import sys

def main():
  symbols = sys.argv[1:]
  for symbol in symbols:
    process(symbol)

if __name__ == "__main__":
  main()
