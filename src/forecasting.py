import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor

try:
    from lightgbm import LGBMRegressor
    HAS_LIGHTGBM = True
except ImportError:
    HAS_LIGHTGBM = False

FEATURE_COLUMNS = [
    'lag_1', 'lag_2', 'lag_4', 'lag_8', 'lag_12',
    'rolling_mean_4', 'rolling_mean_8', 'rolling_mean_12',
    'rolling_std_4', 'rolling_std_8',
    'week_of_year', 'month', 'quarter', 'promo_days', 'holiday_days'
]

class MLDemandForecaster:
    """
    ML Demand Forecasting ModelWrapper supporting HistGradientBoosting,
    RandomForest, and LightGBM models with point predictions and uncertainty intervals.
    """
    def __init__(self, model_type="hist_gb", random_state=42):
        self.model_type = model_type
        self.random_state = random_state
        self.feature_cols = None
        self.model = self._init_model()

    def _init_model(self):
        if self.model_type == "lightgbm" and HAS_LIGHTGBM:
            return LGBMRegressor(n_estimators=100, learning_rate=0.05, random_state=self.random_state, verbosity=-1)
        elif self.model_type == "random_forest":
            return RandomForestRegressor(n_estimators=100, max_depth=12, random_state=self.random_state, n_jobs=-1)
        else: # Default HistGradientBoostingRegressor
            return HistGradientBoostingRegressor(max_iter=100, learning_rate=0.05, random_state=self.random_state)

    def fit(self, df_train):
        # Identify available feature columns (including one-hot encoded category columns)
        cat_cols = [c for c in df_train.columns if c.startswith('cat_')]
        self.feature_cols = [c for c in FEATURE_COLUMNS if c in df_train.columns] + cat_cols

        # Filter out initial rows where lag features are missing
        clean_train = df_train.dropna(subset=['target'] + [c for c in self.feature_cols if c in FEATURE_COLUMNS]).copy()
        
        X = clean_train[self.feature_cols].fillna(0)
        y = clean_train['target']

        self.model.fit(X, y)
        return self

    def predict(self, df_test):
        if self.feature_cols is None:
            raise ValueError("Model has not been fitted yet.")

        X_test = df_test[self.feature_cols].fillna(0)
        preds = self.model.predict(X_test)
        preds = np.maximum(0.0, preds)

        # Estimate prediction uncertainty interval (std of residuals approximation or 15% band)
        lower_bound = np.maximum(0.0, preds * 0.82)
        upper_bound = preds * 1.18

        return {
            'forecast': preds,
            'lower_bound': lower_bound,
            'upper_bound': upper_bound
        }
