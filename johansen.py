import dataset
import numpy as np
import matplotlib.pyplot as plt

db = dataset.connect('sqlite:///C:\\Users\\codch\\cryptocompare.db')
table_name = 'historical_minutes_ohlcv'
exchange = 'Binance'
starting_from = 1564215600

fsym1 = "BTC"
tsym1 = "USD"

result1 = db.query("SELECT * FROM {} WHERE fsym = '{}' AND tsym = '{}' AND time > '{}' ORDER BY time ASC".format(table_name, fsym1, tsym1, starting_from))
result1 = list(result1)

fsym2 = "ETH"
tsym2 = "USD"

result2 = db.query("SELECT * FROM {} WHERE fsym = '{}' AND tsym = '{}' AND time > '{}' ORDER BY time ASC".format(table_name, fsym2, tsym2, starting_from))
result2 = list(result2)

start_time = max(result1[0]['time'], result2[0]['time'])
end_time = min (result1[-1]['time'], result2[-1]['time'])

start_idx_1 = next(i for i in range(len(result1)) if result1[i]['time'] == start_time)
start_idx_2 = next(i for i in range(len(result2)) if result2[i]['time'] == start_time)

end_idx_1 = next(i for i in range(len(result1)) if result1[i]['time'] == end_time)
end_idx_2 = next(i for i in range(len(result2)) if result2[i]['time'] == end_time)

from datetime import datetime
times = list(map(lambda x: datetime.fromtimestamp(x['time']), result1[start_idx_1:end_idx_1 + 1]))
result1 = map(lambda x: x['close'], result1[start_idx_1:end_idx_1 + 1])
result2 = map(lambda x: x['close'], result2[start_idx_2:end_idx_2 + 1])

# fig, ax = plt.subplots()
# r1 = np.diff(np.asarray(list(result2)), 1)
# ax.plot(times[1:], r1)
# plt.show()
# from statsmodels.tsa.stattools import adfuller
# result = adfuller(r1)
# print(result)
# exit()

data = np.asarray(list(zip(result2, result1)))
print(data.shape)

from statsmodels.tsa.vector_ar.vecm import coint_johansen
# johansen_result = coint_johansen(data, 0, 2)
# print("Trace stats are: {}".format(johansen_result.lr1)) # trace stat
# print("Trace stats critical values are: {}".format(johansen_result.cvt)) # trace critical values
# print("Max eigen stats are: {}".format(johansen_result.lr2)) # max eigen stat
# print("Max eigen stats critical values are: {}".format(johansen_result.cvm)) # max eigen critical values

# print("Eigen values: {}".format(johansen_result.eig))
# print("Eigen vectors: {}".format(johansen_result.evec))


# portfolio = np.dot(data, johansen_result.evec[0])

# fig, ax = plt.subplots()
# ax.plot(times, portfolio)
# plt.show()

from statsmodels.tsa.vector_ar.vecm import VECM, select_order, select_coint_rank
# print(select_order(data, 50, deterministic="co").summary())
# print(select_coint_rank(data, 0, 43).summary())
model = VECM(data, deterministic="co", k_ar_diff=1)
res = model.fit()
print("Alpha: {}".format(res.alpha))
print("Beta: {}".format(res.beta)) # cointegration vector
print(np.dot(res.alpha, np.transpose(res.beta)))
print("Gamma: {}".format(res.gamma))
print(res.sigma_u)
print(res.det_coef_coint)
print("Residual: {}".format(res.resid))
print(res.det_coef)

from statsmodels.tsa.stattools import adfuller
coint_series = np.dot(data, res.beta).reshape(9999,)
result = adfuller(coint_series)
print(result)

fig, ax = plt.subplots()
ax.plot(times, np.dot(data, res.beta))
plt.show()