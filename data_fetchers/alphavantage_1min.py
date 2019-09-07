import dataset
import urllib.request
import functools
import json

# Alphavantage time is the END time of the period

base_url = "https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&interval=1min&outputsize=full&apikey=GEGM4SX2DR9VJB68"

def get_full(symbol):
  url = base_url + "&symbol={}".format(symbol)
  print("requesting with {}...".format(url))
  response = urllib.request.urlopen(url).read()
  print("responded")
  parsed_response = json.loads(response.decode('utf-8'))

  from dateutil.parser import parse
  from dateutil.tz import gettz
  timezone = parsed_response["Meta Data"]["6. Time Zone"]
  results = []
  for t, p in parsed_response["Time Series (1min)"].items():
    t = "{} T".format(t)
    ts = int(parse(t, tzinfos={ "T": gettz(timezone) }).timestamp())
    results.append({
      'time': ts,
      'open': p["1. open"],
      'high': p["2. high"],
      'low': p["3. low"],
      'close': p["4. close"],
      'volume': p["5. volume"]
    })
  print("response size: {}".format(len(results)))
  return results

db = dataset.connect('sqlite:///C:\\Users\\codch\\alphavantage.db')
table_name = 'historical_minutes_ohlcv'

def write_to_db(data_points, symbol):
  table = db[table_name]
  for idx, data_point in enumerate(data_points):
    if (idx % 100 == 0):
      print("writing row {}...".format(idx + 1))
    table.insert_ignore({**data_point, **{'symbol': symbol}}, ['time', 'symbol'])

def process(symbol):
  write_to_db(get_full(symbol), symbol)

import sys

def main():
  symbols = sys.argv[1:]
  for symbol in symbols:
    process(symbol)

if __name__ == "__main__":
  main()
