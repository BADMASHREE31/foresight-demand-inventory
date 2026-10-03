import pandas as pd
import numpy as np

def build_weekly_sku_dataset(processed_data):
    """
    Aggregates daily sales to Weekly SKU level (W-MON grain) and builds
    prior-only lag, rolling, and calendar features with zero future leakage.
    """
    sales_df = processed_data['sales_daily'].copy()
    sku_df = processed_data['sku_master'].copy()
    cal_df = processed_data['calendar'].copy()

    sales_df['date'] = pd.to_datetime(sales_df['date'])
    cal_df['date'] = pd.to_datetime(cal_df['date'])

    # Merge daily sales with calendar info
    sales_merged = sales_df.merge(cal_df[['date', 'week', 'month', 'season', 'is_holiday', 'promo_event']], on='date', how='left')

    # Assign weekly end/start date (Weekly alignment on Monday)
    sales_merged['week_date'] = sales_merged['date'].dt.to_period('W-MON').dt.start_time

    # Aggregate to Weekly-SKU grain
    weekly_df = sales_merged.groupby(['sku_id', 'week_date']).agg(
        weekly_units=('units_sold', 'sum'),
        weekly_revenue=('revenue', 'sum'),
        avg_price=('unit_price', 'mean'),
        promo_days=('promo_flag', 'sum'),
        holiday_days=('is_holiday', 'sum')
    ).reset_index()

    # Join SKU Master metadata
    weekly_df = weekly_df.merge(
        sku_df[['sku_id', 'category', 'subcategory', 'unit_cost', 'list_price']],
        on='sku_id',
        how='left'
    )

    # Sort chronologically per SKU for lag calculation
    weekly_df = weekly_df.sort_values(['sku_id', 'week_date']).reset_index(drop=True)

    # Build Lags & Rolling Features per SKU (SHIFT BY 1 FIRST to prevent leakage!)
    feature_dfs = []

    for sku_id, group in weekly_df.groupby('sku_id'):
        grp = group.copy()
        
        # Target variable
        grp['target'] = grp['weekly_units']

        # Shifted base (value at t-1)
        shifted = grp['weekly_units'].shift(1)

        # 1. Lag Features (all derived from shifted series)
        grp['lag_1'] = grp['weekly_units'].shift(1)
        grp['lag_2'] = grp['weekly_units'].shift(2)
        grp['lag_4'] = grp['weekly_units'].shift(4)
        grp['lag_8'] = grp['weekly_units'].shift(8)
        grp['lag_12'] = grp['weekly_units'].shift(12)
        grp['lag_52'] = grp['weekly_units'].shift(52)

        # 2. Rolling Statistics (min_periods=1 to preserve records where possible)
        grp['rolling_mean_4'] = shifted.rolling(window=4, min_periods=1).mean()
        grp['rolling_mean_8'] = shifted.rolling(window=8, min_periods=1).mean()
        grp['rolling_mean_12'] = shifted.rolling(window=12, min_periods=1).mean()
        
        grp['rolling_std_4'] = shifted.rolling(window=4, min_periods=1).std().fillna(0)
        grp['rolling_std_8'] = shifted.rolling(window=8, min_periods=1).std().fillna(0)

        # 3. Calendar Features
        grp['week_of_year'] = grp['week_date'].dt.isocalendar().week.astype(int)
        grp['month'] = grp['week_date'].dt.month
        grp['quarter'] = grp['week_date'].dt.quarter

        feature_dfs.append(grp)

    df_features = pd.concat(feature_dfs, ignore_index=True)

    # One-hot encode category for ML models
    df_features = pd.get_dummies(df_features, columns=['category'], prefix='cat', drop_first=False)

    return df_features
