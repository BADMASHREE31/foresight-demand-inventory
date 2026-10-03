import numpy as np
import pandas as pd

class SeasonalNaivePredictor:
    """
    Seasonal-Naive Baseline Predictor.
    Predicts demand equal to the same week from the previous year (lag_52),
    falling back to recent rolling 4-week mean (lag_4) or lag_1 if 52 weeks unavailable.
    """
    def __init__(self, season_lag=52, fallback_lag=4):
        self.season_lag = season_lag
        self.fallback_lag = fallback_lag

    def predict(self, df_features):
        """
        Generates predictions for each row in df_features based on prior historical lags.
        No training parameter needed.
        """
        preds = []
        for idx, row in df_features.iterrows():
            # Check lag_52 first
            val = row.get('lag_52', np.nan)
            if pd.isna(val) or val is None:
                # Fallback to rolling mean or lag_4 or lag_1
                val = row.get('rolling_mean_4', row.get('lag_1', 0.0))
            if pd.isna(val) or val is None:
                val = 0.0
            preds.append(max(0.0, float(val)))
        return np.array(preds)
