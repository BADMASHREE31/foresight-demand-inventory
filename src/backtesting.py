import pandas as pd
import numpy as np
from src.baseline import SeasonalNaivePredictor
from src.forecasting import MLDemandForecaster
from src.metrics import evaluate_all_metrics

def run_rolling_origin_backtest(df_weekly_features, horizon_weeks=8, num_windows=4, step_weeks=4):
    """
    Executes honest rolling-origin time-series cross-validation.
    Compares Seasonal-Naive Baseline against Candidate ML Models.
    No data leakage guaranteed.
    """
    unique_weeks = sorted(df_weekly_features['week_date'].unique())
    total_weeks = len(unique_weeks)

    if total_weeks < horizon_weeks + (num_windows * step_weeks) + 12:
        num_windows = max(1, (total_weeks - horizon_weeks - 12) // step_weeks)

    results = []

    for w in range(num_windows):
        # Calculate split point index from the end
        cutoff_idx = total_weeks - horizon_weeks - ((num_windows - 1 - w) * step_weeks)
        cutoff_date = unique_weeks[cutoff_idx]
        test_end_date = unique_weeks[min(cutoff_idx + horizon_weeks - 1, total_weeks - 1)]

        train_mask = df_weekly_features['week_date'] < cutoff_date
        test_mask = (df_weekly_features['week_date'] >= cutoff_date) & (df_weekly_features['week_date'] <= test_end_date)

        train_df = df_weekly_features[train_mask].copy()
        test_df = df_weekly_features[test_mask].copy()

        if len(test_df) == 0 or len(train_df) == 0:
            continue

        actuals = test_df['target'].values

        # 1. Baseline Model Forecast
        baseline_model = SeasonalNaivePredictor()
        baseline_preds = baseline_model.predict(test_df)
        baseline_metrics = evaluate_all_metrics(actuals, baseline_preds)

        # 2. HistGradientBoosting ML Forecast
        ml_hist = MLDemandForecaster(model_type="hist_gb")
        ml_hist.fit(train_df)
        ml_hist_preds = ml_hist.predict(test_df)['forecast']
        ml_hist_metrics = evaluate_all_metrics(actuals, ml_hist_preds)

        # 3. RandomForest ML Forecast
        ml_rf = MLDemandForecaster(model_type="random_forest")
        ml_rf.fit(train_df)
        ml_rf_preds = ml_rf.predict(test_df)['forecast']
        ml_rf_metrics = evaluate_all_metrics(actuals, ml_rf_preds)

        results.append({
            'window': w + 1,
            'cutoff_date': str(cutoff_date)[:10],
            'test_end_date': str(test_end_date)[:10],
            'test_samples': len(actuals),
            'baseline_wape': baseline_metrics['WAPE'],
            'hist_gb_wape': ml_hist_metrics['WAPE'],
            'rf_wape': ml_rf_metrics['WAPE'],
            'baseline_metrics': baseline_metrics,
            'hist_gb_metrics': ml_hist_metrics,
            'rf_metrics': ml_rf_metrics
        })

    # Summary table across all windows
    avg_baseline_wape = np.mean([r['baseline_wape'] for r in results])
    avg_hist_gb_wape = np.mean([r['hist_gb_wape'] for r in results])
    avg_rf_wape = np.mean([r['rf_wape'] for r in results])

    comparison_summary = [
        {
            'Model': 'Seasonal-Naive Baseline',
            'WAPE': round(avg_baseline_wape, 4),
            'MAE': round(np.mean([r['baseline_metrics']['MAE'] for r in results]), 4),
            'RMSE': round(np.mean([r['baseline_metrics']['RMSE'] for r in results]), 4),
            'Bias': round(np.mean([r['baseline_metrics']['Bias'] for r in results]), 4)
        },
        {
            'Model': 'HistGradientBoosting',
            'WAPE': round(avg_hist_gb_wape, 4),
            'MAE': round(np.mean([r['hist_gb_metrics']['MAE'] for r in results]), 4),
            'RMSE': round(np.mean([r['hist_gb_metrics']['RMSE'] for r in results]), 4),
            'Bias': round(np.mean([r['hist_gb_metrics']['Bias'] for r in results]), 4)
        },
        {
            'Model': 'RandomForest',
            'WAPE': round(avg_rf_wape, 4),
            'MAE': round(np.mean([r['rf_metrics']['MAE'] for r in results]), 4),
            'RMSE': round(np.mean([r['rf_metrics']['RMSE'] for r in results]), 4),
            'Bias': round(np.mean([r['rf_metrics']['Bias'] for r in results]), 4)
        }
    ]

    df_summary = pd.DataFrame(comparison_summary)

    # Model Selection Rule
    best_ml_wape = min(avg_hist_gb_wape, avg_rf_wape)
    best_ml_name = "HistGradientBoosting" if avg_hist_gb_wape <= avg_rf_wape else "RandomForest"

    if best_ml_wape < avg_baseline_wape * 0.98: # Requires at least 2% improvement to beat baseline
        final_model_name = best_ml_name
        improvement_pct = round(((avg_baseline_wape - best_ml_wape) / avg_baseline_wape) * 100.0, 2)
        selection_status = "BEATS BASELINE"
        final_wape = best_ml_wape
    else:
        final_model_name = "Seasonal-Naive Baseline"
        improvement_pct = 0.0
        selection_status = "BASELINE RETAINED"
        final_wape = avg_baseline_wape

    selection_metadata = {
        'final_model': final_model_name,
        'final_wape': final_wape,
        'baseline_wape': avg_baseline_wape,
        'improvement_pct': improvement_pct,
        'status': selection_status,
        'summary_table': df_summary.to_dict(orient='records'),
        'window_details': results
    }

    return selection_metadata, df_summary
