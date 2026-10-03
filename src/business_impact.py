import pandas as pd
import numpy as np

def calculate_business_impact(risk_df, sku_master_df):
    """
    Quantifies financial impact in Rupees:
    1. Revenue at Risk (lost sales from stockouts)
    2. Capital Locked in Excess Stock (working capital tied up)
    """
    merged = risk_df.merge(
        sku_master_df[['sku_id', 'unit_cost', 'list_price']],
        on='sku_id',
        how='left'
    )

    merged['unit_cost'] = merged['unit_cost'].fillna(100.0)
    merged['list_price'] = merged['list_price'].fillna(150.0)

    # 1. Revenue at Risk Calculation
    # Unfulfilled units = max(0, lead_time_demand - (on_hand + on_order))
    available_stock = merged['on_hand_units'] + merged['on_order_units']
    unfulfilled_units = np.maximum(0.0, merged['lead_time_demand'] - available_stock)
    revenue_at_risk = unfulfilled_units * merged['list_price']

    # 2. Capital Locked Calculation
    # Excess units = max(0, on_hand - (1.5 * forecast_8w_demand))
    excess_threshold = merged['forecast_8w_demand'] * 1.5
    excess_units = np.maximum(0.0, merged['on_hand_units'] - excess_threshold)
    capital_locked = excess_units * merged['unit_cost']

    merged['unfulfilled_units_risk'] = unfulfilled_units.round(1)
    merged['revenue_at_risk'] = revenue_at_risk.round(2)
    merged['excess_units'] = excess_units.round(1)
    merged['capital_locked'] = capital_locked.round(2)
    merged['inventory_value'] = (merged['on_hand_units'] * merged['unit_cost']).round(2)

    # Total Business Summary
    total_summary = {
        'total_skus': len(merged),
        'total_revenue_at_risk': float(merged['revenue_at_risk'].sum()),
        'total_capital_locked': float(merged['capital_locked'].sum()),
        'total_inventory_value': float(merged['inventory_value'].sum()),
        'total_unfulfilled_units': float(merged['unfulfilled_units_risk'].sum()),
        'total_excess_units': float(merged['excess_units'].sum()),
        'reorder_skus_count': int((merged['recommended_action'] == 'REORDER NOW').sum()),
        'markdown_skus_count': int((merged['recommended_action'] == 'MARKDOWN / CLEAR').sum()),
        'investigate_skus_count': int((merged['recommended_action'] == 'INVESTIGATE').sum()),
        'healthy_skus_count': int((merged['recommended_action'] == 'HEALTHY').sum())
    }

    return merged, total_summary
