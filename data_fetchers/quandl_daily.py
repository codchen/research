import dataset
import urllib.request
import functools
import json

base_url = "https://www.quandl.com/api/v3/datasets/{}/data.json?api_key=TJt6NLigz1kBgmBb3DZ7"
# to filter by dates curl "https://www.quandl.com/api/v3/datasets/WIKI/FB.json?column_index=4&start_date=2014-01-01&end_date=2014-12-31&collapse=monthly&transform=rdiff&api_key=YOURAPIKEY"
# symbol can be found at https://blog.quandl.com/api-for-commodity-data

def get(symbol):
  url = base_url.format(symbol)
  print("requesting with {}...".format(url))
  response = urllib.request.urlopen(url).read()
  print("responded")
  parsed_response = json.loads(response.decode('utf-8'))

  from dateutil.parser import parse
  from dateutil.tz import gettz
  timezone = 'US/Eastern'
  results = []
  for d in parsed_response["dataset_data"]["data"]:
    t = "{} 17:00:00 T".format(d[0])
    ts = int(parse(t, tzinfos={ "T": gettz(timezone) }).timestamp())
    results.append({
      'time': ts,
      'open': d[1],
      'high': d[2],
      'low': d[3],
      'close': d[4],
      'settle': d[6],
      'volume': d[7],
      'prev_day_open_interest': d[8]
    })
  print("response size: {}".format(len(results)))
  return results

db = dataset.connect('sqlite:///C:\\Users\\codch\\quandl.db')
table_name = 'historical_daily_ohlcv'

def write_to_db(data_points, symbol):
  table = db[table_name]
  for idx, data_point in enumerate(data_points):
    if (idx % 100 == 0):
      print("writing row {}...".format(idx + 1))
    table.insert_ignore({**data_point, **{'symbol': symbol}}, ['time', 'symbol'])

def process(symbol):
  write_to_db(get(symbol), symbol)

process('CHRIS/CME_CL1')