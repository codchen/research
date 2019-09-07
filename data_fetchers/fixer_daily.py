import dataset
import urllib.request
import functools
import json
from datetime import datetime, timedelta
from dateutil.parser import parse
from dateutil.tz import gettz

db = dataset.connect('sqlite:///C:\\Users\\codch\\fixer.db')
table_name = 'historical_daily_ohlcv'
table = db[table_name]

base_url = "http://data.fixer.io/api/{}?access_key=15f6b52b74cb7c7f35859b002355237d&base=USD&symbols=EUR,GBP,CAD,JPY,AUD,NZD,CHF"

start = '2019-08-26'
end = '2019-08-28'
current = start
while current != end:
  url = base_url.format(current)
  print("requesting with {}...".format(url))
  response = urllib.request.urlopen(url).read()
  parsed_response = json.loads(response.decode('utf-8'))
  print(parsed_response)
  timezone = 'US/Eastern'
  t = "{} 17:00:00 T".format(parsed_response['date'])
  ts = int(parse(t, tzinfos={ "T": gettz(timezone) }).timestamp())
  print('writing...')
  table.insert_ignore({ 'time': ts, 'symbol': 'EUR', 'rate': parsed_response['rates']['EUR'] }, ['time', 'symbol'])
  table.insert_ignore({ 'time': ts, 'symbol': 'GBP', 'rate': parsed_response['rates']['GBP'] }, ['time', 'symbol'])
  table.insert_ignore({ 'time': ts, 'symbol': 'CAD', 'rate': parsed_response['rates']['CAD'] }, ['time', 'symbol'])
  table.insert_ignore({ 'time': ts, 'symbol': 'JPY', 'rate': parsed_response['rates']['JPY'] }, ['time', 'symbol'])
  table.insert_ignore({ 'time': ts, 'symbol': 'AUD', 'rate': parsed_response['rates']['AUD'] }, ['time', 'symbol'])
  table.insert_ignore({ 'time': ts, 'symbol': 'NZD', 'rate': parsed_response['rates']['NZD'] }, ['time', 'symbol'])
  table.insert_ignore({ 'time': ts, 'symbol': 'CHF', 'rate': parsed_response['rates']['CHF'] }, ['time', 'symbol'])
  current = (datetime.strptime(current , '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
