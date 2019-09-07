import dataset
import urllib.request
import functools
import json

exchange = 'Binance'
base_url = "https://min-api.cryptocompare.com/data/histominute?fsym={}&tsym={}&e={}&limit=2000&api_key=8d45fa03c39c3e737316e082dda56899a5dd7bacde9f46bf1efeeb32e9d241ab"

def get_full(fsym, tsym, offset):
  url = base_url.format(fsym, tsym, exchange)
  if offset is not None:
    url = "{}&toTs={}".format(url, offset)
  print("requesting with {}...".format(url))
  response = urllib.request.urlopen(url).read()
  print("responded")
  parsed_response = json.loads(response.decode('utf-8'))
  results = parsed_response['Data']
  print("response size: {}".format(len(results)))
  return results

db = dataset.connect('sqlite:///C:\\Users\\codch\\cryptocompare.db')
table_name = 'historical_minutes_ohlcv'

def write_to_db(data_points, fsym, tsym):
  table = db[table_name]
  for idx, data_point in enumerate(data_points):
    if (idx % 100 == 0):
      print("writing row {}...".format(idx + 1))
    table.insert_ignore({**data_point, **{'fsym': fsym, 'tsym': tsym, 'exchange': exchange}}, ['time', 'fsym', 'tsym', 'exchange'])

def process(fsym, tsym):
  offset = None
  for i in range(5):
    result = get_full(fsym, tsym, offset)
    offset = result[0]['time']
    write_to_db(result, fsym, tsym)

import sys

def main():
  tsym = sys.argv[1]
  symbols = sys.argv[2:]
  for symbol in symbols:
    process(symbol, tsym)

if __name__ == "__main__":
  main()
