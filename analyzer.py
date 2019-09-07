
import math
import numpy as np
import matplotlib.pyplot as plt

from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.vector_ar.vecm import VECM, select_order, select_coint_rank

from tsutil import string_to_timestamp

def analyze(df, start_time, end_time, symbols):
  file_name = "{}_{}_{}_coint_series".format(
    '_'.join(list(map(lambda s: s.replace('/', '_'), symbols))),
    start_time if isinstance(start_time, int) else start_time.replace(' ', '_'),
    end_time if isinstance(end_time, int) else end_time.replace(' ', '_')
  )

  results = {
    'symbols': str(symbols),
    'ts_start': start_time if isinstance(start_time, int) else string_to_timestamp(start_time),
    'ts_end': end_time if isinstance(end_time, int) else string_to_timestamp(end_time)
  }

  data = df.to_numpy()
  max_order = int(data.shape[0] / 8)
  select_order_res = select_order(data, max_order, deterministic="ci")
  # print(select_order_res.summary())
  selected_aic_order = select_order_res.selected_orders['aic']
  results['selected_order'] = selected_aic_order
  select_coint_rank_result = select_coint_rank(data, 0, selected_aic_order)
  print(select_coint_rank_result.summary())
  selected_coint_rank = 0
  for i in range(len(select_coint_rank_result.test_stats)):
    if select_coint_rank_result.test_stats[i] < select_coint_rank_result.crit_vals[i]:
      selected_coint_rank = i
      break
  results['selected_rank'] = selected_coint_rank
  if selected_coint_rank != 0:
    model = VECM(data, deterministic="ci", k_ar_diff=selected_aic_order, coint_rank=selected_coint_rank)
    res = model.fit()
    results['cointegrated_alpha'] = np.array2string(res.alpha.flatten())
    results['cointegrated_beta'] = np.array2string(res.beta.flatten())
    results['cointegrated_constant'] = res.det_coef_coint.flatten()[0]
    cointegrated_series = np.dot(data, res.beta).flatten() + results['cointegrated_constant']
    cointegrated_mean = np.mean(cointegrated_series)
    results['cointegrated_mean'] = cointegrated_mean
    cointegrated_std = np.std(cointegrated_series)
    results['cointegrated_std'] = cointegrated_std
    max_deviation = np.amax(np.absolute(cointegrated_series - cointegrated_mean))
    results['cointegrated_max_deviation'] = max_deviation

    adf_res = adfuller(cointegrated_series, maxlag=max_order, store=True, regresults=True)
    cointegrated_adf_p_value = adf_res[1]
    results['cointegrated_adf_p_value'] = cointegrated_adf_p_value
    cointegrated_adf_lag = adf_res[3].usedlag
    results['cointegrated_adf_lag'] = cointegrated_adf_lag
    cointegrated_half_life = -math.log(2) / adf_res[3].resols.params[0]
    results['cointegrated_half_life'] = cointegrated_half_life

    fig, ax = plt.subplots()
    ax.plot(df.index.to_numpy(), cointegrated_series)
    path = "figures/{}.png".format(file_name)
    results['cointegrated_series_img_path'] = path
    plt.savefig(path)
  with open("results/{}.txt".format(file_name), "w") as result_file:
    result_file.write("{}".format(results))
  return results

# from dataloader import load_data

# dataframe = load_data('2019-07-28', '2019-07-29', ['BTC', 'ETH'], [])
# print(analyze(dataframe, '2019-07-28', '2019-07-29', ['BTC', 'ETH']))