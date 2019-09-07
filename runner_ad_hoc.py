import dataset
import pandas as pd 

alpha_db = dataset.connect('sqlite:///C:\\Users\\codch\\alphavantage.db')
quandl_db = dataset.connect('sqlite:///C:\\Users\\codch\\quandl.db')

ts_start = 1514930400
ts_end = 1566853200
stock_symbol = 'RDS-A'
stock_symbol_2 = 'SPY'
future_symbol = 'CHRIS/CME_CL1'
symbols = ['RDS-A', 'SPY', 'CHRIS/CME_CL1']
dbs = [alpha_db, alpha_db, quandl_db]

result_dicts = []
for i in range(len(symbols)):
  symbol = symbols[i]
  db = dbs[i]
  query = "SELECT * FROM historical_daily_ohlcv WHERE symbol = '{}' AND time >= '{}' AND time < '{}'".format(symbol, ts_start, ts_end)
  result = list(db.query(query))
  if db == quandl_db:
    result_dict = { row['time']: float(row['settle']) for row in result }
    del result_dict[1544047200] # stock market closed on 2018-12-05 in honor of Bush's death
  else:
    result_dict = { row['time']: float(row['close']) for row in result }
  result_dicts.append(result_dict)
all_ts = sorted(result_dicts[0].keys())
results = { 'timestamp': all_ts }
for i in range(len(symbols)):
  symbol = symbols[i]
  result_dict = result_dicts[i]
  results[symbol] = list(
    map(
      lambda ts: result_dict[ts] if ts in result_dict.keys() else float('nan'), all_ts
    )
  )
df = pd.DataFrame(results)
df.set_index('timestamp', inplace=True)
from analyzer import analyze
print(analyze(df, ts_start, ts_end, symbols))