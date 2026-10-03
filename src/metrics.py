import numpy as np

def calculate_wape(y_true, y_pred):
    """
    Calculates Weighted Absolute Percentage Error (WAPE).
    WAPE = sum(|actual - forecast|) / sum(|actual|)
    """
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    total_actual = np.sum(np.abs(y_true))
    if total_actual == 0:
        return 0.0
    return float(np.sum(np.abs(y_true - y_pred)) / total_actual)

def calculate_mae(y_true, y_pred):
    """Calculates Mean Absolute Error (MAE)."""
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    return float(np.mean(np.abs(y_true - y_pred)))

def calculate_rmse(y_true, y_pred):
    """Calculates Root Mean Squared Error (RMSE)."""
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))

def calculate_bias(y_true, y_pred):
    """
    Calculates Forecast Bias (Mean Signed Forecast Error).
    Bias = mean(forecast - actual)
    Positive bias indicates over-forecasting, negative indicates under-forecasting.
    """
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    return float(np.mean(y_pred - y_true))

def evaluate_all_metrics(y_true, y_pred):
    """Returns dictionary of all evaluation metrics."""
    return {
        'WAPE': round(calculate_wape(y_true, y_pred), 4),
        'MAE': round(calculate_mae(y_true, y_pred), 4),
        'RMSE': round(calculate_rmse(y_true, y_pred), 4),
        'Bias': round(calculate_bias(y_true, y_pred), 4)
    }
