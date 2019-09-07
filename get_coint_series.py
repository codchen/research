import math
import dataset
import numpy as np
import matplotlib.pyplot as plt
from functools import reduce

from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.vector_ar.vecm import VECM, select_order, select_coint_rank

fig, ax = plt.subplots()

db = dataset.connect('sqlite:///C:\\Users\\codch\\cryptocompare.db')
table_name = 'historical_minutes_ohlcv'
exchange = 'Binance'
start_date = '2019-07-27'
end_date = '2019-08-03'
symbols = ['BTC','ETH','BCH']
fiat = 'USDT'

def get_prices(symbol):
  from dateutil.parser import parse

  query = "SELECT * FROM {} WHERE fsym = '{}' AND tsym = '{}' AND exchange = '{}' AND time > '{}' AND time < '{}' ORDER BY time ASC".format(
    table_name,
    symbol,
    fiat,
    exchange,
    parse(start_date).timestamp(),
    parse(end_date).timestamp()
  )
  return list(db.query(query))

prices = list(map(lambda s: get_prices(s), symbols))
start_times = list(map(lambda price: price[0]['time'], prices))
end_times = list(map(lambda price: price[-1]['time'], prices))
start_time = reduce(lambda t1, t2: max(t1, t2), start_times)
end_time = reduce(lambda t1, t2: min(t1, t2), end_times)
start_indices = list(map(lambda price: next(i for i in range(len(price)) if price[i]['time'] == start_time), prices))
end_indices = list(map(lambda price: next(i for i in range(len(price)) if price[i]['time'] == end_time), prices))

sliced_prices = list(map(lambda price_with_idx: price_with_idx[1][start_indices[price_with_idx[0]]:end_indices[price_with_idx[0]] + 1], enumerate(prices)))
data = np.asarray(list(map(lambda price: list(map(lambda p: p['close'], price)), sliced_prices)))
times = list(map(lambda p: p['time'], sliced_prices[0]))
for series in data:
  results = adfuller(series.reshape(len(series,)), store=True, regresults=True)
  print(results[0:3])
  print(results[3].usedlag)
  print(results[3].resols.summary())
  print(-math.log(2) / results[3].resols.params[0])

exit()

data_to_fit = data.transpose()
print(select_order(data_to_fit, 50, deterministic="co").selected_orders)
print(select_coint_rank(data_to_fit, 0, 15).test_stats)
# exit()
model = VECM(data_to_fit, deterministic="co", k_ar_diff=15)
res = model.fit()

ax.plot(times, np.dot(data_to_fit, res.beta))
plt.show()
