import pytest
import numpy as np
import pandas as pd
from src.metrics import calculate_wape, calculate_mae, calculate_rmse, calculate_bias
from src.baseline import SeasonalNaivePredictor

def test_wape_calculation_exact():
    y_true = [100, 200, 300]
    y_pred = [110, 190, 310]
    # abs errors: 10 + 10 + 10 = 30. total actual: 600. WAPE = 30 / 600 = 0.05
    wape = calculate_wape(y_true, y_pred)
    assert pytest.approx(wape, 0.001) == 0.05

def test_metrics_formulas():
    y_true = [10, 20]
    y_pred = [12, 18]
    assert calculate_mae(y_true, y_pred) == 2.0
    assert calculate_bias(y_true, y_pred) == 0.0

def test_seasonal_naive_baseline():
    df_test = pd.DataFrame({
        'lag_52': [50.0, np.nan],
        'rolling_mean_4': [40.0, 30.0],
        'lag_1': [45.0, 28.0]
    })
    predictor = SeasonalNaivePredictor()
    preds = predictor.predict(df_test)
    assert len(preds) == 2
    assert preds[0] == 50.0
    assert preds[1] == 30.0
