import dataset
import numpy as np

db = dataset.connect('sqlite:///C:\\Users\\codch\\cryptocompare.db')
table_name = 'historical_hourly_ohlcv'

fsym1 = "BTC"
tsym1 = "USD"

result1 = db.query("SELECT * FROM {} WHERE fsym = '{}' AND tsym = '{}' ORDER BY time ASC".format(table_name, fsym1, tsym1))
result1 = list(result1)

fsym2 = "ETH"
tsym2 = "USD"

result2 = db.query("SELECT * FROM {} WHERE fsym = '{}' AND tsym = '{}' ORDER BY time ASC".format(table_name, fsym2, tsym2))
result2 = list(result2)

start_time = max(result1[0]['time'], result2[0]['time'])
end_time = min (result1[-1]['time'], result2[-1]['time'])

# start_idx_1 = next(i for i in range(len(result1)) if result1[i]['time'] == start_time)
# start_idx_2 = next(i for i in range(len(result2)) if result2[i]['time'] == start_time)
start_idx_1 = 29200
start_idx_2 = 29200

end_idx_1 = next(i for i in range(len(result1)) if result1[i]['time'] == end_time)
end_idx_2 = next(i for i in range(len(result2)) if result2[i]['time'] == end_time)

from datetime import datetime
times = list(map(lambda x: datetime.fromtimestamp(x['time']), result1[start_idx_1:end_idx_1 + 1]))
result1 = map(lambda x: x['close'], result1[start_idx_1:end_idx_1 + 1])
result2 = map(lambda x: x['close'], result2[start_idx_2:end_idx_2 + 1])

from sklearn.linear_model import LinearRegression
X = np.asarray(list(result1))
X = X.reshape(len(X), 1)
y = np.asarray(list(result2))
print(X[0:10])
print(y[0:10])
reg = LinearRegression().fit(X, y)
print(reg.coef_)
print(reg.intercept_)

import matplotlib.pyplot as plt
res = y - (X.flatten() * reg.coef_ + reg.intercept_)

fig, ax = plt.subplots()
ax.plot(times, res)
plt.show()