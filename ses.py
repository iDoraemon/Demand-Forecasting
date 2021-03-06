import numpy as np
import pandas as pd
from scipy.optimize import fmin_l_bfgs_b
from statsmodels.tools import eval_measures


# --------------------------------------------------------------------------


def RMSE(params, *args):
    data_frame = args[0]
    alpha = params

    rmse = 0

    forecast = [0] * data_frame.count()

    forecast[1] = data_frame.iloc[0]

    for index in range(2, data_frame.count()):
        forecast[index] = alpha * data_frame.iloc[index - 1] + (1 - alpha) * forecast[index - 1]

    rmse = eval_measures.rmse(forecast[1:], data_frame[1:])

    return rmse


# --------------------------------------------------------------------------


def simple_exponential_smoothing(dataframe, next_periods, alpha=None):
    # Datetime format
    date_format = '%b-%y'

    # Get size of original dataframe
    size = dataframe.count()

    # Create ahead-day entries in future
    date_range = pd.date_range(start=dataframe.index[0], periods=size + next_periods, format=date_format, freq='MS')

    # Create new dataframe for forecasting
    forecast_full_frame = pd.Series(data=[np.nan] * (len(date_range)), index=date_range)

    if alpha is None:
        initial_values = np.array([0.0])
        boundaries = [(0, 1)]

        parameters = fmin_l_bfgs_b(RMSE, x0=initial_values, args=(dataframe, next_periods), bounds=boundaries,
                                   approx_grad=True)
        alpha = parameters[0]

    # Begin forecasting
    for idx in range(len(forecast_full_frame.index) - 1):
        if idx == 0:
            forecast_full_frame.iloc[idx + 1] = dataframe.iloc[idx]
        elif idx < size:
            forecast_full_frame.iloc[idx + 1] = alpha * dataframe.iloc[idx] + (1 - alpha) * forecast_full_frame.iloc[
                idx]
        else:
            forecast_full_frame.iloc[idx + 1] = forecast_full_frame.iloc[idx]

    # Drop all NaN values
    forecast_full_frame.dropna(inplace=True)

    # Future timeframe only
    forecast_partial_frame = forecast_full_frame[~forecast_full_frame.index.isin(dataframe.index)]

    # Root mean squared error
    rmse = eval_measures.rmse(dataframe[1:size], forecast_full_frame[0:size - 1])

    # Return result
    return forecast_full_frame, forecast_partial_frame, rmse, alpha

# --------------------------------------------------------------------------
