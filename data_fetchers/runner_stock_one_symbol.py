import json
import time
from alphavantage_1min import process as alpha_process
from alphavantage_daily import process as alpha_process_daily
from iex_1min import process as iex_process

# alpha_process('RDS-A')
# iex_process('RDS.A')
alpha_process_daily('SPY')