from dataloader import load_data
from analyzer import analyze

# both crypto and stocks okay
def intraday_working_hour_only(stock_symbols, crypto_symbols, date):
  start_time = "{} 09:30:00".format(date)
  end_time = "{} 16:00:00".format(date)
  df = load_data(
    start_time,
    end_time,
    crypto_symbols,
    stock_symbols,
    True
  )
  analysis = analyze(df, start_time, end_time, stock_symbols + crypto_symbols)
  print(analysis)

# crypto only
def intraday(symbols, date):
  pass

# crypto only
def hourly_two_weeks(symbols, end_date=None):
  pass

# both crypto and stocks okay
def daily_six_months(symbols, end_date=None):
  pass

# both crypto and stocks okay
def daily_one_year(symbols, end_date=None):
  pass

# intraday_working_hour_only([], ['ETH','BTC'], '2019-08-16')
from statsmodels.tsa.vector_ar.vecm import _endog_matrices
import numpy as np

crypto_symbols = ['BTC','ETH']
start_time = "2019-08-16 16:00:00"
end_time = "2019-08-16 16:30:00"
df1 = load_data(
  start_time,
  end_time,
  crypto_symbols,
  [],
  True
)
start_time = "2019-08-16 15:00:00"
end_time = "2019-08-16 15:30:00"
df2 = load_data(
  start_time,
  end_time,
  crypto_symbols,
  [],
  True
)
from statsmodel_extensions.vecm import select_order
endog_list = np.asarray([df1.to_numpy(), df2.to_numpy()])
exog_list = np.asarray([np.ones((len(df1.to_numpy()), 1)), np.ones((len(df2.to_numpy()), 1))])
maxlags = 5
print(select_order(endog_list, exog_list, maxlags))
