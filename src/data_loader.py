import os
import pandas as pd
from src.config import RAW_DATA_DIR

REQUIRED_SCHEMAS = {
    'sales_daily': ['date', 'sku_id', 'units_sold', 'revenue', 'unit_price', 'promo_flag'],
    'sku_master': ['sku_id', 'category', 'subcategory', 'launch_date', 'unit_cost', 'list_price'],
    'calendar': ['date', 'week', 'month', 'season', 'is_holiday', 'promo_event'],
    'inventory_snapshots': ['date', 'sku_id', 'on_hand_units', 'on_order_units', 'lead_time_days', 'reorder_point']
}

def load_raw_data(data_dir=RAW_DATA_DIR):
    """
    Loads all raw extracts from data_dir and validates basic schema presence.
    Returns dictionary of DataFrames.
    """
    data = {}
    validation_reports = {}

    for name, required_cols in REQUIRED_SCHEMAS.items():
        file_path = os.path.join(data_dir, f"{name}.csv")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Required raw extract file missing: {file_path}")

        df = pd.read_csv(file_path)
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        validation_reports[name] = {
            'rows': len(df),
            'cols': len(df.columns),
            'missing_cols': missing_cols,
            'is_valid': len(missing_cols) == 0
        }

        if len(missing_cols) > 0:
            raise ValueError(f"Extract '{name}' missing required columns: {missing_cols}")

        data[name] = df

    return data, validation_reports
