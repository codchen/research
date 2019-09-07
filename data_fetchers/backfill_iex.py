import json
import time
from iex_1min import process as iex_process

import pandas as pd
from pandas.tseries.offsets import BDay

for i in range(3, 24):
  date = (pd.datetime.today() - BDay(i)).to_pydatetime().strftime('%Y%m%d')
  with open('symbols.json') as json_file:
    data = json.load(json_file)
    for symbol in data['stock']:
      start = time.time()

      iex_process(symbol, date)

      elapsed = time.time() - start
      if elapsed < 5:
        time.sleep(5 - elapsed)
