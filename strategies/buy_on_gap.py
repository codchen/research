from tsutil import timestamp_to_string, timestamp_to_date, string_to_date

import numpy as np

def backtest(sorted_close_prices_by_symbols, sorted_open_prices_by_symbols, timestamps):
  capital = 1.0
  diffs = {}
  trades = {}
  trades_to_dates = {}
  stats_per_date = {}
  longest_timestamps = []
  max_days = 0
  for symbol, prices in sorted_close_prices_by_symbols.items():
    diffs[symbol] = np.diff(prices) * (-1)
    trades[symbol] = [-1] * len(prices)
    trades_to_dates[symbol] = []
    max_days = max(max_days, len(prices))
    if len(timestamps[symbol]) > len(longest_timestamps):
      longest_timestamps = timestamps[symbol]

  for i in range(0, max_days):
    return_ratios = {}
    for symbol, returns in diffs.items():
      if i + 90 > len(returns):
        continue
      std = np.std(returns[i:i + 90])
      twenty_ma = np.mean(sorted_close_prices_by_symbols[symbol][i + 1:i + 21])
      open_price = sorted_open_prices_by_symbols[symbol][i]
      gap = open_price - sorted_close_prices_by_symbols[symbol][i + 1]
      if open_price > twenty_ma and gap < -std:
        return_ratios[symbol] = gap / std
    selected_symbols = sorted(return_ratios.keys(), key=lambda symbol: return_ratios[symbol])[:10]
    for symbol in selected_symbols:
      trades[symbol][i] = -return_ratios[symbol]
    returns = list(
      map(
        lambda symbol: (sorted_close_prices_by_symbols[symbol][i] - sorted_open_prices_by_symbols[symbol][i]) / sorted_open_prices_by_symbols[symbol][i],
        selected_symbols
      )
    )
    date = timestamp_to_string(longest_timestamps[i])
    if len(returns) == 0:
      stats_per_date[timestamp_to_string(longest_timestamps[i])] = ()
    else:
      stats_per_date[timestamp_to_string(longest_timestamps[i])] = (date, len(returns), np.mean(returns), max(returns), min(returns))

  for i in range(max_days - 1, -1, -1):
    selected_symbols = []
    for symbol, trade in trades.items():
      if i >= len(trade):
        continue
      if trade[i] > 0:
        selected_symbols.append(symbol)
        trades_to_dates[symbol].append(
          (
            timestamp_to_string(timestamps[symbol][i]),
            trade[i],
            (sorted_close_prices_by_symbols[symbol][i] - sorted_open_prices_by_symbols[symbol][i]) / sorted_open_prices_by_symbols[symbol][i]
          )
        )

    if len(selected_symbols) == 0:
      continue
    capital_per_symbol = capital / len(selected_symbols)
    for symbol in selected_symbols:
      capital += capital_per_symbol * (sorted_close_prices_by_symbols[symbol][i] - sorted_open_prices_by_symbols[symbol][i]) / sorted_open_prices_by_symbols[symbol][i]
  statistics = {}
  for symbol, results in trades_to_dates.items():
    if len(results) == 0:
      continue
    statistics[symbol] = (
      len(results),
      np.mean(list(map(lambda res: res[2], results))),
      np.std(list(map(lambda res: res[2], results))),
      min(list(map(lambda res: res[2], results)))
    )
  filtered_daily_stats = list(filter(lambda stats: len(stats) > 0, stats_per_date.values()))
  filtered_daily_returns = list(map(lambda stats: stats[2], filtered_daily_stats))
  aggregated_stats = (
    np.mean(filtered_daily_returns),
    np.std(filtered_daily_returns),
    min(filtered_daily_stats, key=lambda stats: stats[2])
  )
  return capital, trades_to_dates, statistics, aggregated_stats

def validate_daily_data(timestamp_list):
  exemptions = []
  with open('../data/market_close_dates.json') as json_file:
    data = json.load(json_file)
    exemptions = data['stock']
  exemptions = list(map(lambda s: string_to_date(s), exemptions))
  import pandas as pd
  from pandas.tseries.offsets import BDay
  sorted_timestamp_list = sorted(timestamp_list)
  date_list = list(map(timestamp_to_date, sorted_timestamp_list))
  first_day_str = timestamp_to_string(sorted_timestamp_list[0])
  last_day_str = timestamp_to_string(sorted_timestamp_list[-1])
  expected_dates = pd.date_range(first_day_str, last_day_str, freq=BDay()).date
  ptr1 = 0
  ptr2 = 0
  while ptr1 < len(date_list) and ptr2 < len(expected_dates):
    if expected_dates[ptr2] in exemptions:
      if date_list[ptr1] == expected_dates[ptr2]:
        print("Date {} is supposed to be exempted".format(date_list[ptr1]))
        ptr1 += 1
        ptr2 += 1
      else:
        ptr2 += 1
    elif date_list[ptr1] == expected_dates[ptr2]:
      ptr1 += 1 
      ptr2 += 1
    elif date_list[ptr1] < expected_dates[ptr2]:
      print("Date {} not in expected dates".format(date_list[ptr1]))
      ptr1 += 1
    else:
      print("Expected date {} not found".format(expected_dates[ptr2]))
      ptr2 += 1

def segment_timeseries(opens, closes):
  sorted_opens = opens[::-1]
  sorted_closes = closes[::-1]
  ma_20 = np.mean(sorted_closes[:90])
  results = []
  start, end = [], []
  for i in range(21, len(sorted_opens)):
    new_ma_20 = np.mean(sorted_closes[i - 20:i])
    if sorted_opens[i - 1] < ma_20 and sorted_opens[i] > new_ma_20:
      start.append(i)
    elif sorted_opens[i - 1] > ma_20 and sorted_opens[i] < new_ma_20 and len(start) > 0:
      end.append(i)
    ma_20 = new_ma_20
  return list(zip(start, end))


import dataset
import json
alpha_db = dataset.connect('sqlite:///C:\\Users\\codch\\alphavantage.db')
sorted_close_prices_by_symbols = {}
sorted_open_prices_by_symbols = {}
timestamps = {}
with open('../data/nasdaq_100.json') as json_file:
  data = json.load(json_file)
  for symbol in data['current']:
    query = "SELECT * FROM historical_daily_adjusted_ohlcv WHERE symbol = '{}' ORDER BY time DESC".format(symbol)
    query_result = list(alpha_db.query(query))
    sorted_close_prices_by_symbols[symbol] = list(map(lambda res: float(res['close']), query_result))
    sorted_open_prices_by_symbols[symbol] = list(map(lambda res: float(res['open']), query_result))
    timestamps[symbol] = list(map(lambda res: int(res['time']), query_result))

# print(segment_timeseries(sorted_open_prices_by_symbols['AAPL'], sorted_close_prices_by_symbols['AAPL']))
from statsmodels.tsa.stattools import adfuller
segments = list(
  filter(
    lambda seg: seg[1] - seg[0] > 5,
    segment_timeseries(sorted_open_prices_by_symbols['AAPL'], sorted_close_prices_by_symbols['AAPL'])
  )
)
opens = sorted_open_prices_by_symbols['AAPL'][::-1]
closes = sorted_close_prices_by_symbols['AAPL'][::-1]
for segment in segments:
  data = []
  for i in range(segment[0], segment[1]):
    data.append(opens[i])
    data.append(closes[i])
  print("{}: {}".format(segment, adfuller(data, regression='ct')))

# for symbol, time in timestamps.items():
#   print("Validating {}".format(symbol))
#   validate_daily_data(time)

# print(backtest(sorted_close_prices_by_symbols, sorted_open_prices_by_symbols, timestamps))