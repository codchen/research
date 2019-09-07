import numpy as np

from .var import estimate_var

def select_order(endog_list, exog_list, maxlags):
  lag_with_min_aic = -1
  min_aic = float("inf")
  # lag here is lag in level-VAR, which is lag in diff-VECM + 1
  for lag in range(1, maxlags + 2):
    info_criteria = estimate_var(endog_list, exog_list, lag)
    if info_criteria['aic'] < min_aic:
      min_aic = info_criteria['aic']
      lag_with_min_aic = lag - 1 # adjust back to lag in diff-VECM
  return lag_with_min_aic, min_aic
