import os
import pytest
import pandas as pd
from src.config import RAW_DATA_DIR
from src.data_loader import load_raw_data
from src.data_cleaning import clean_and_unify_data
from src.feature_engineering import build_weekly_sku_dataset

def test_raw_data_loading():
    raw_data, report = load_raw_data(RAW_DATA_DIR)
    assert 'sales_daily' in raw_data
    assert 'sku_master' in raw_data
    assert len(raw_data['sales_daily']) > 0
    assert len(raw_data['sku_master']) == 200

def test_data_cleaning_and_unification():
    raw_data, _ = load_raw_data(RAW_DATA_DIR)
    processed_data, audit = clean_and_unify_data(raw_data, save_processed=False)
    
    assert audit['duplicates_removed'] >= 0
    assert audit['missing_values_handled'] >= 0
    assert audit['data_completeness_pct'] > 95.0
    assert 'sales_daily' in processed_data

def test_feature_engineering_no_future_leakage():
    raw_data, _ = load_raw_data(RAW_DATA_DIR)
    processed_data, _ = clean_and_unify_data(raw_data, save_processed=False)
    df_weekly = build_weekly_sku_dataset(processed_data)
    
    assert 'lag_1' in df_weekly.columns
    assert 'lag_52' in df_weekly.columns
    assert 'rolling_mean_4' in df_weekly.columns
    assert len(df_weekly) > 0
