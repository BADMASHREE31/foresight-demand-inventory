import os
import sys
import json
import pickle
import pandas as pd
import numpy as np

# Ensure root workspace is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config import RAW_DATA_DIR, PROCESSED_DATA_DIR, MODEL_ARTIFACTS_DIR, FORECAST_HORIZON_WEEKS
from src.data_loader import load_raw_data
from src.data_cleaning import clean_and_unify_data
from src.feature_engineering import build_weekly_sku_dataset
from src.backtesting import run_rolling_origin_backtest
from src.baseline import SeasonalNaivePredictor
from src.forecasting import MLDemandForecaster
from src.risk_scoring import score_inventory_risks
from src.business_impact import calculate_business_impact

def execute_pipeline():
    print("==================================================")
    print("      PROJECT FORESIGHT - PIPELINE EXECUTION      ")
    print("==================================================")

    # 1. Load Raw Data
    print("\n[Step 1/7] Ingesting Raw Client Extracts...")
    raw_data, validation_report = load_raw_data(RAW_DATA_DIR)
    print(f"-> Ingested {len(raw_data['sales_daily'])} daily sales rows across {len(raw_data['sku_master'])} SKUs.")

    # 2. Clean & Unify
    print("\n[Step 2/7] Cleaning & Unifying Datasets...")
    processed_data, audit_report = clean_and_unify_data(raw_data, save_processed=True)
    print(f"-> Removed {audit_report['duplicates_removed']} duplicates, fixed {audit_report['invalid_values_fixed']} invalid values.")
    print(f"-> Overall Data Completeness: {audit_report['data_completeness_pct']}%")

    # 3. Feature Engineering
    print("\n[Step 3/7] Building Weekly Prior-Only Features...")
    df_weekly_features = build_weekly_sku_dataset(processed_data)
    print(f"-> Created {len(df_weekly_features)} weekly SKU records with prior-only lag & rolling features.")

    # 4. Rolling-Origin Backtesting
    print("\n[Step 4/7] Running Rolling-Origin Cross-Validation Backtest...")
    selection_metadata, df_summary = run_rolling_origin_backtest(df_weekly_features, horizon_weeks=FORECAST_HORIZON_WEEKS)
    print("\n--- MODEL COMPARISON TABLE ---")
    print(df_summary.to_string(index=False))
    print(f"\n-> Final Model Selected: {selection_metadata['final_model']}")
    print(f"-> Model Status: {selection_metadata['status']} (WAPE: {selection_metadata['final_wape']:.4f} vs Baseline: {selection_metadata['baseline_wape']:.4f})")

    # 5. Fit Selected Model & Produce 8-Week Forecasts
    print("\n[Step 5/7] Generating 8-Week SKU Demand Forecasts...")
    last_week_date = df_weekly_features['week_date'].max()
    future_weeks = [last_week_date + pd.Timedelta(weeks=w) for w in range(1, FORECAST_HORIZON_WEEKS + 1)]

    all_skus = df_weekly_features['sku_id'].unique()
    forecast_rows = []

    if selection_metadata['final_model'] == "Seasonal-Naive Baseline":
        model_obj = SeasonalNaivePredictor()
        # Forecast each SKU
        for sku in all_skus:
            sku_feats = df_weekly_features[df_weekly_features['sku_id'] == sku].tail(FORECAST_HORIZON_WEEKS)
            preds = model_obj.predict(sku_feats)
            for i, fw in enumerate(future_weeks[:len(preds)]):
                p_val = preds[i]
                forecast_rows.append({
                    'sku_id': sku,
                    'forecast_week': fw.strftime('%Y-%m-%d'),
                    'forecast': round(float(p_val), 2),
                    'lower_bound': round(float(max(0, p_val * 0.8)), 2),
                    'upper_bound': round(float(p_val * 1.2), 2),
                    'model': 'Seasonal-Naive Baseline'
                })
    else:
        # Fit chosen ML Model on full historical data
        model_type_key = "hist_gb" if "HistGradientBoosting" in selection_metadata['final_model'] else "random_forest"
        ml_forecaster = MLDemandForecaster(model_type=model_type_key)
        ml_forecaster.fit(df_weekly_features)

        # For prediction over horizon, iterate forward recursively or using latest lag features
        for sku in all_skus:
            sku_latest = df_weekly_features[df_weekly_features['sku_id'] == sku].tail(FORECAST_HORIZON_WEEKS).copy()
            if len(sku_latest) == 0:
                continue
            pred_dict = ml_forecaster.predict(sku_latest)
            preds = pred_dict['forecast']
            lowers = pred_dict['lower_bound']
            uppers = pred_dict['upper_bound']

            for i, fw in enumerate(future_weeks[:len(preds)]):
                forecast_rows.append({
                    'sku_id': sku,
                    'forecast_week': fw.strftime('%Y-%m-%d'),
                    'forecast': round(float(preds[i]), 2),
                    'lower_bound': round(float(lowers[i]), 2),
                    'upper_bound': round(float(uppers[i]), 2),
                    'model': selection_metadata['final_model']
                })

    df_forecast = pd.DataFrame(forecast_rows)
    print(f"-> Generated {len(df_forecast)} forecast points across {len(all_skus)} SKUs.")

    # 6. Inventory Risk Engine
    print("\n[Step 6/7] Scoring Inventory Stockout & Overstock Risks...")
    df_risk = score_inventory_risks(df_forecast, processed_data['inventory_snapshots'], processed_data['sku_master'])
    
    # 7. Financial Business Impact
    print("\n[Step 7/7] Computing Business Impact & Rupee Value at Stake...")
    df_impact, total_summary = calculate_business_impact(df_risk, processed_data['sku_master'])
    
    print("\n==================================================")
    print("             EXECUTIVE BUSINESS IMPACT            ")
    print("==================================================")
    print(f"Total SKUs Evaluated     : {total_summary['total_skus']}")
    print(f"Estimated Revenue at Risk : Rs. {total_summary['total_revenue_at_risk']:,.2f}")
    print(f"Estimated Capital Locked  : Rs. {total_summary['total_capital_locked']:,.2f}")
    print(f"Reorder Now Candidates    : {total_summary['reorder_skus_count']} SKUs")
    print(f"Markdown / Clear Candidates: {total_summary['markdown_skus_count']} SKUs")
    print(f"Healthy SKUs              : {total_summary['healthy_skus_count']} SKUs")
    print("==================================================")

    # Save Pipeline Outputs
    df_weekly_features.to_csv(os.path.join(PROCESSED_DATA_DIR, 'weekly_features.csv'), index=False)
    df_forecast.to_csv(os.path.join(PROCESSED_DATA_DIR, 'forecast_outputs.csv'), index=False)
    df_impact.to_csv(os.path.join(PROCESSED_DATA_DIR, 'risk_impact_matrix.csv'), index=False)

    with open(os.path.join(MODEL_ARTIFACTS_DIR, 'selection_metadata.json'), 'w') as f:
        json.dump(selection_metadata, f, indent=4)

    with open(os.path.join(MODEL_ARTIFACTS_DIR, 'audit_report.json'), 'w') as f:
        json.dump(audit_report, f, indent=4)

    with open(os.path.join(MODEL_ARTIFACTS_DIR, 'business_summary.json'), 'w') as f:
        json.dump(total_summary, f, indent=4)

    print(f"\nPipeline successfully completed! Processed data saved in '{PROCESSED_DATA_DIR}'.\n")

if __name__ == '__main__':
    execute_pipeline()
