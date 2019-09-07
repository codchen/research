import dataset
import numpy as np

# db = dataset.connect('sqlite:///C:\\Users\\codch\\cryptocompare.db')
# table_name = 'historical_hourly_ohlcv'

# fsym1 = "BTC"
# tsym1 = "USD"

# result1 = db.query("SELECT * FROM {} WHERE fsym = '{}' AND tsym = '{}' ORDER BY time ASC".format(table_name, fsym1, tsym1))
# result1 = list(result1)

# fsym2 = "ETH"
# tsym2 = "USD"

# result2 = db.query("SELECT * FROM {} WHERE fsym = '{}' AND tsym = '{}' ORDER BY time ASC".format(table_name, fsym2, tsym2))
# result2 = list(result2)

# start_time = max(result1[0]['time'], result2[0]['time'])
# end_time = min (result1[-1]['time'], result2[-1]['time'])

# # start_idx_1 = next(i for i in range(len(result1)) if result1[i]['time'] == start_time)
# # start_idx_2 = next(i for i in range(len(result2)) if result2[i]['time'] == start_time)
# start_idx_1 = 29200
# start_idx_2 = 29200

# end_idx_1 = next(i for i in range(len(result1)) if result1[i]['time'] == end_time)
# end_idx_2 = next(i for i in range(len(result2)) if result2[i]['time'] == end_time)

# from datetime import datetime
# times = list(map(lambda x: datetime.fromtimestamp(x['time']), result1[start_idx_1:end_idx_1 + 1]))
# result1 = map(lambda x: x['close'], result1[start_idx_1:end_idx_1 + 1])
# result2 = map(lambda x: x['close'], result2[start_idx_2:end_idx_2 + 1])

# data1 = np.diff(np.asarray(list(result1)), 1)
# data2 = np.diff(np.asarray(list(result2)), 1)

# import matplotlib.pyplot as plt

# fig, ax = plt.subplots()
# ax.plot(times[1:], data2)
# plt.show()

import math
import dataset
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from functools import reduce

# from statsmodels.tsa.stattools import adfuller
# from statsmodels.tsa.vector_ar.vecm import VECM, select_order, select_coint_rank

# db = dataset.connect('sqlite:///C:\\Users\\codch\\cryptocompare.db')
# table_name = 'historical_minutes_ohlcv'
# exchange = 'Binance'
# start_date = '2019-07-27'
# symbols = ['BSV']
# fiat = 'USDT'

# plt.ion()
# fig, ax = plt.subplots()

# def get_prices(symbol):
#   from dateutil.parser import parse

#   query = "SELECT * FROM {} WHERE fsym = '{}' AND tsym = '{}' AND exchange = '{}' AND time > '{}' ORDER BY time ASC".format(
#     table_name,
#     symbol,
#     fiat,
#     exchange,
#     parse(start_date).timestamp()
#   )
#   return list(db.query(query))

# prices = list(map(lambda s: get_prices(s), symbols))
# start_times = list(map(lambda price: price[0]['time'], prices))
# end_times = list(map(lambda price: price[-1]['time'], prices))
# start_time = reduce(lambda t1, t2: max(t1, t2), start_times)
# end_time = reduce(lambda t1, t2: min(t1, t2), end_times)
# start_indices = list(map(lambda price: next(i for i in range(len(price)) if price[i]['time'] == start_time), prices))
# end_indices = list(map(lambda price: next(i for i in range(len(price)) if price[i]['time'] == end_time), prices))

# sliced_prices = list(map(lambda price_with_idx: price_with_idx[1][start_indices[price_with_idx[0]]:end_indices[price_with_idx[0]] + 1], enumerate(prices)))
# data = np.asarray(list(map(lambda price: list(map(lambda p: p['close'], price)), sliced_prices)))
# times = list(map(lambda p: p['time'], sliced_prices[0]))
# for series in data:
#   flattened = series.reshape(len(series,))
#   for i in range(7):
#     start = i * 1440
#     end = min((i + 1) * 1440, len(series))
#     segment = flattened[start:end]
#     print("From {}({}) to {}({})".format(times[start], datetime.fromtimestamp(times[start]), times[end - 1], datetime.fromtimestamp(times[end - 1])))
#     ax.plot(times[start:end], segment)
#     plt.draw()
#     results = adfuller(segment, store=True, regresults=True)
#     print(results[0:3])
#     print(results[3].usedlag)
#     print(results[3].resols.summary())
#     print(-math.log(2) / results[3].resols.params[0])

# plt.ioff()
# plt.show()
# plt.imshow(plt.imread('figures/BTC_ETH_2019-07-28_2019-07-29_coint_series.png'))
# plt.axis('off')
# plt.show()

from statsmodels.tsa.vector_ar import util
from statsmodels.tsa.vector_ar.var_model import VAR
from dataloader import load_data

crypto_symbols = ['BTC','ETH']
start_time = "2019-08-16 16:00:00"
end_time = "2019-08-16 16:30:00"
df = load_data(
  start_time,
  end_time,
  crypto_symbols,
  [],
  True
)

data = df.to_numpy()
exog = []
exog.append(np.ones(len(data)).reshape(-1, 1))
exog = np.hstack(exog)
var_model = VAR(data, exog)
k_trend = util.get_trendorder('c')
n_totobs = len(data)
p = 1
maxlags = 5
n_totobs = len(data)
lags = p
offset = maxlags + 1 - p
nobs = n_totobs - lags - offset
data = data[offset:]
exog = exog[offset:]
print(data)
Z = np.array([data[t-lags : t][::-1].ravel() for t in range(lags, len(data))])
print(Z)
z = util.get_var_endog(data, lags, trend='c',  has_constant='raise')
print(z.shape)
exit()

x = util.get_var_endog(exog[-nobs:], 0, trend="nc", has_constant="raise")
x_inst = exog[-nobs:]
x = np.column_stack((x, x_inst))

temp_z = z
z = np.empty((x.shape[0], x.shape[1]+z.shape[1]))
z[:, :k_trend] = temp_z[:, :k_trend]
z[:, k_trend:k_trend+x.shape[1]] = x
z[:, k_trend+x.shape[1]:] = temp_z[:, k_trend:]
y_sample = data[lags:]
params = np.linalg.lstsq(z, y_sample, rcond=1e-15)[0]
print(z.shape)
print(y_sample.shape)
print(params)