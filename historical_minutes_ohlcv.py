import dataset
import urllib.request
import functools
import json

base_url = "https://min-api.cryptocompare.com/data/histominute?"
# BTC ETH EOS LTC BCH *BCG *DGD NEO BSV
fsym = "BTC"
tsym = "USDT"
exchange = "Binance"
base_params = {
  "fsym": fsym,
  "tsym": tsym,
  "e": exchange,
  "limit": 2000,
  "api_key": "8d45fa03c39c3e737316e082dda56899a5dd7bacde9f46bf1efeeb32e9d241ab"
}
db = dataset.connect('sqlite:///C:\\Users\\codch\\cryptocompare.db')
table_name = 'historical_minutes_ohlcv'

def get_parsed_result(offset):
  params = base_params
  if (offset is not None):
    params = {**params, **{"toTs": offset}}
  url = functools.reduce(lambda url, key: "{}{}={}&".format(url, key, params[key]), params, base_url)[:-1]
  print("requesting with {}...".format(url))
  response = urllib.request.urlopen(url).read()
  print("responded")

  parsed_response = json.loads(response.decode('utf-8'))

  # Each data point looks like
  # {'time': 1563863220, 'close': 10036.72, 'high': 10070.58, 'low': 10033, 'open': 10043.5,
  # 'volumefrom': 192.78, 'volumeto': 1937278.74}
  # volumefrom means the unit of fsym traded
  # volumeto means the unit of tsym traded
  return parsed_response['Data']

def write_to_db(data_points):
  table = db[table_name]
  for idx, data_point in enumerate(data_points):
    if (idx % 100 == 0):
      print("writing row {}...".format(idx + 1))
    table.insert_ignore({**data_point, **{'fsym': fsym, 'tsym': tsym, 'exchange': exchange}}, ['time', 'fsym', 'tsym'])

offset = None
for i in range(5):
  print("Iter {}...".format(i))
  data_points = get_parsed_result(offset)
  offset = data_points[0]['time']
  write_to_db(data_points)
