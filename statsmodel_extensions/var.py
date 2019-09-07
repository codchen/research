import numpy as np

from statsmodels.tsa.vector_ar import util
from statsmodels.tools.linalg import logdet_symm

def format_data_for_estimate_var(endog_list, exog_list, lag):
  k_trend = 1

  explanatory_data = []
  target_data = []
  for i in range(len(endog_list)):
    endog = endog_list[i]
    exog = None
    if len(exog_list) > 0:
      exog = exog_list[i]
    nobs = len(endog) - lag

    if exog is not None and len(endog) != len(exog):
      raise ValueError("Endog has length {} but exog has length {} - i={}".format(len(endog), len(exog), i))
    if nobs <= 0:
      raise ValueError("Endog only has {} observations but requesting with {} lags - i={}".format(len(endog), lag, i))

    useful_endog = endog[-nobs-lag:]
    z = util.get_var_endog(useful_endog, lag, has_constant='raise')

    if exog is not None:
      useful_exog = exog[-nobs:]
      x = util.get_var_endog(useful_exog, 0, trend='nc', has_constant='raise')
      x = np.column_stack((x, useful_exog))
      temp_z = z
      z = np.empty((x.shape[0], x.shape[1]+z.shape[1]))
      z[:, :k_trend] = temp_z[:, :k_trend]
      z[:, k_trend:k_trend+x.shape[1]] = x
      z[:, k_trend+x.shape[1]:] = temp_z[:, k_trend:]

    for i in range(k_trend):
      if (np.diff(z[:, i]) == 1).all():  # modify the trend-column
          z[:, i] += lag
      # make the same adjustment for the quadratic term
      if (np.diff(np.sqrt(z[:, i])) == 1).all():
          z[:, i] = (np.sqrt(z[:, i]) + lag)**2

    explanatory_data.extend(z)
    target_data.extend(endog[-nobs:])
  return target_data, explanatory_data

def info_criteria(resid, nobs, endog_num_features, exog_num_features, lag):
  k_trend = 1

  k_exog = k_trend + exog_num_features
  free_params = lag * endog_num_features ** 2 + endog_num_features * k_exog
  df_model = endog_num_features * lag + k_exog
  df_resid = nobs - df_model
  sse = np.dot(resid.T, resid)
  sigma_u = sse / df_resid

  ld = logdet_symm(sigma_u * df_resid / nobs)

  # See Lütkepohl pp. 146-150

  aic = ld + (2. / nobs) * free_params
  bic = ld + (np.log(nobs) / nobs) * free_params
  hqic = ld + (2. * np.log(np.log(nobs)) / nobs) * free_params
  fpe = ((nobs + df_model) / df_resid) ** endog_num_features * np.exp(ld)

  return {
    'aic': aic,
    'bic': bic,
    'hqic': hqic,
    'fpe': fpe
  }

def estimate_var(endog_list, exog_list, lag):
  target_data, explanatory_data = format_data_for_estimate_var(endog_list, exog_list, lag)
  params = np.linalg.lstsq(explanatory_data, target_data, rcond=1e-15)[0]
  resid = target_data - np.dot(explanatory_data, params)
  endog_num_features = endog_list[0].shape[1]
  exog_num_features = 0
  if len(exog_list) > 0 and len(exog_list[0].shape) > 1:
    exog_num_features = exog_list[0].shape[1]
  return info_criteria(resid, len(target_data), endog_num_features, exog_num_features, lag)

