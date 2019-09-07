import json
import time
from alphavantage_1min import process as alpha_process
from cryptocompare_1min import process as crypto_process
from iex_1min import process as iex_process

def run(run_alpha, run_crypto, run_iex):
  with open('symbols.json') as json_file:
    data = json.load(json_file)
    for symbol in data['stock']:
      start = time.time()

      if run_alpha:
        alpha_process(symbol)

      if run_iex:
        iex_process(symbol)

      elapsed = time.time() - start
      if elapsed < 12 and (run_alpha or run_iex):
        time.sleep(12 - elapsed)

    for symbol in data['crypto']:
      start = time.time()

      if run_crypto:
        crypto_process(symbol, 'USDT')

      elapsed = time.time() - start
      if elapsed < 1 and run_crypto:
        time.sleep(1 - elapsed)

def run_nasdaq():
  from alphavantage_daily import process as alpha_process_daily
  with open('../data/nasdaq_100.json') as json_file:
    data = json.load(json_file)
    for symbol in data['current']:
      start = time.time()
      alpha_process_daily(symbol, True)
      elapsed = time.time() - start
      if elapsed < 12:
        time.sleep(12 - elapsed)

# run(True, True, True)
run_nasdaq()
