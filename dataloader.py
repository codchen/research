from tsutil import string_to_timestamp

import dataset
import pandas as pd 

crypto_db = dataset.connect('sqlite:///C:\\Users\\codch\\cryptocompare.db')
alpha_db = dataset.connect('sqlite:///C:\\Users\\codch\\alphavantage.db')
iex_db = dataset.connect('sqlite:///C:\\Users\\codch\\iex.db')

def load_data(start_time, end_time, crypto_symbols, stock_symbols, use_iex=False):
  ts_start = string_to_timestamp(start_time)
  ts_end = string_to_timestamp(end_time)
  all_ts = list(range(ts_start, ts_end, 60))
  results = { 'timestamp': all_ts }
  for crypto_symbol in crypto_symbols:
    query = "SELECT * FROM historical_minutes_ohlcv WHERE fsym = '{}' AND tsym = 'USDT' AND time >= '{}' AND time < '{}'".format(crypto_symbol, ts_start, ts_end)
    result = list(crypto_db.query(query))
    result_dict = { row['time']: row['close'] for row in result }
    results[crypto_symbol] = list(
      map(
        lambda ts: result_dict[ts] if ts in result_dict.keys() else float('nan'), all_ts
      )
    )
  for stock_symbol in stock_symbols:
    query = "SELECT * FROM historical_minutes_ohlcv WHERE symbol = '{}' AND time >= '{}' AND time < '{}'".format(stock_symbol, ts_start, ts_end)
    result = list((iex_db if use_iex else alpha_db).query(query))
    result_dict = { row['time']: row['close'] for row in result }
    results[stock_symbol] = list(
      map(
        lambda ts: result_dict[ts] if ts in result_dict.keys() else float('nan'), all_ts
      )
    )
  df = pd.DataFrame(results)
  df.set_index('timestamp', inplace=True)
  return df

# res = load_data('2019-08-07 00:00:00', '2019-08-09 15:00:00', ['BTC'], ['QQQ'])