import os
import pandas as pd
import numpy as np
from src.config import PROCESSED_DATA_DIR, CATEGORY_MAPPING

def clean_and_unify_data(raw_data, save_processed=True):
    """
    Cleans raw extracts, standardizes categories, handles missing/duplicate values,
    and returns processed datasets along with an audit trail report.
    """
    sales_df = raw_data['sales_daily'].copy()
    sku_df = raw_data['sku_master'].copy()
    cal_df = raw_data['calendar'].copy()
    inv_df = raw_data['inventory_snapshots'].copy()

    audit_report = {
        'initial_sales_rows': len(sales_df),
        'initial_sku_count': len(sku_df),
        'initial_inventory_rows': len(inv_df),
        'duplicates_removed': 0,
        'missing_values_handled': 0,
        'invalid_values_fixed': 0,
        'unmatched_skus': [],
        'categories_normalized': 0,
        'cleaning_decisions': []
    }

    # 1. Deduplication
    dup_count = sales_df.duplicated().sum()
    if dup_count > 0:
        sales_df = sales_df.drop_duplicates().reset_index(drop=True)
        audit_report['duplicates_removed'] = int(dup_count)
        audit_report['cleaning_decisions'].append(
            f"Removed {dup_count} duplicate sales transactions."
        )

    # 2. Date Parsing
    sales_df['date'] = pd.to_datetime(sales_df['date'])
    cal_df['date'] = pd.to_datetime(cal_df['date'])
    sku_df['launch_date'] = pd.to_datetime(sku_df['launch_date'])
    inv_df['date'] = pd.to_datetime(inv_df['date'])

    # 3. Handle Category Inconsistencies & Missing Values in SKU Master
    missing_cat_count = sku_df['category'].isna().sum()
    if missing_cat_count > 0:
        sku_df['category'] = sku_df['category'].fillna('Uncategorized')
        audit_report['missing_values_handled'] += int(missing_cat_count)
        audit_report['cleaning_decisions'].append(
            f"Imputed {missing_cat_count} missing category values as 'Uncategorized'."
        )

    # Normalize category names
    def normalize_cat(cat_str):
        if not isinstance(cat_str, str):
            return 'Uncategorized'
        cleaned = cat_str.strip().lower()
        return CATEGORY_MAPPING.get(cleaned, cat_str.strip().title())

    sku_df['category'] = sku_df['category'].apply(normalize_cat)
    audit_report['categories_normalized'] = len(sku_df['category'].unique())

    # 4. Clean Sales Daily (Missing promo_flag & invalid negative units)
    missing_promo = sales_df['promo_flag'].isna().sum()
    if missing_promo > 0:
        sales_df['promo_flag'] = sales_df['promo_flag'].fillna(0).astype(int)
        audit_report['missing_values_handled'] += int(missing_promo)
        audit_report['cleaning_decisions'].append(
            f"Imputed {missing_promo} missing promo_flag records with 0 (no promo)."
        )

    # Fix negative units_sold
    neg_units = (sales_df['units_sold'] < 0).sum()
    if neg_units > 0:
        sales_df['units_sold'] = np.maximum(0, sales_df['units_sold'])
        sales_df['revenue'] = np.maximum(0.0, sales_df['revenue'])
        audit_report['invalid_values_fixed'] += int(neg_units)
        audit_report['cleaning_decisions'].append(
            f"Clipped {neg_units} invalid negative units_sold records to 0."
        )

    # 5. Foreign Key Integrity Check
    master_skus = set(sku_df['sku_id'])
    sales_skus = set(sales_df['sku_id'])
    inv_skus = set(inv_df['sku_id'])

    unmatched_sales = sales_skus - master_skus
    unmatched_inv = master_skus - inv_skus

    audit_report['unmatched_skus'] = list(unmatched_sales)
    audit_report['missing_inventory_skus_count'] = len(unmatched_inv)
    
    if len(unmatched_sales) > 0:
        audit_report['cleaning_decisions'].append(
            f"Found {len(unmatched_sales)} sales SKUs not in SKU Master."
        )

    if len(unmatched_inv) > 0:
        audit_report['cleaning_decisions'].append(
            f"Found {len(unmatched_inv)} active SKUs missing from Inventory Snapshots."
        )

    # Calculate overall data completeness %
    total_expected_cells = sales_df.size + sku_df.size + cal_df.size + inv_df.size
    total_null_cells = (sales_df.isna().sum().sum() + sku_df.isna().sum().sum() + 
                        cal_df.isna().sum().sum() + inv_df.isna().sum().sum())
    
    completeness_pct = round((1.0 - (total_null_cells / total_expected_cells)) * 100.0, 2)
    audit_report['data_completeness_pct'] = completeness_pct

    # Final Processed Datasets
    processed_data = {
        'sales_daily': sales_df,
        'sku_master': sku_df,
        'calendar': cal_df,
        'inventory_snapshots': inv_df
    }

    if save_processed:
        os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
        sales_df.to_csv(os.path.join(PROCESSED_DATA_DIR, 'sales_daily_clean.csv'), index=False)
        sku_df.to_csv(os.path.join(PROCESSED_DATA_DIR, 'sku_master_clean.csv'), index=False)
        cal_df.to_csv(os.path.join(PROCESSED_DATA_DIR, 'calendar_clean.csv'), index=False)
        inv_df.to_csv(os.path.join(PROCESSED_DATA_DIR, 'inventory_snapshots_clean.csv'), index=False)

    return processed_data, audit_report
