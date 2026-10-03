import pandas as pd
import numpy as np
from src.config import STOCKOUT_THRESHOLDS, OVERSTOCK_THRESHOLDS

def score_inventory_risks(forecast_df, inventory_df, sku_master_df, horizon_weeks=8):
    """
    Computes Stockout Risk, Overstock Risk, Actionable Decision Quadrant,
    and attached financial impact per SKU.
    """
    inv_dict = inventory_df.set_index('sku_id').to_dict(orient='index')
    sku_dict = sku_master_df.set_index('sku_id').to_dict(orient='index')

    risk_records = []

    for sku_id, group in forecast_df.groupby('sku_id'):
        inv = inv_dict.get(sku_id, None)
        meta = sku_dict.get(sku_id, {})

        total_8w_forecast = group['forecast'].sum()
        avg_weekly_forecast = total_8w_forecast / float(horizon_weeks)

        if inv is None:
            # Missing inventory snapshot handling
            risk_records.append({
                'sku_id': sku_id,
                'product_name': f"Product {sku_id}",
                'category': meta.get('category', 'Unknown'),
                'subcategory': meta.get('subcategory', 'Unknown'),
                'on_hand_units': 0,
                'on_order_units': 0,
                'lead_time_days': 14,
                'reorder_point': 0,
                'forecast_8w_demand': round(total_8w_forecast, 2),
                'lead_time_demand': round(avg_weekly_forecast * 2.0, 2),
                'stockout_coverage': 0.0,
                'overstock_ratio': 0.0,
                'stockout_risk_level': 'HIGH',
                'overstock_risk_level': 'LOW',
                'stockout_risk_score': 0.9,
                'overstock_risk_score': 0.1,
                'recommended_action': 'INVESTIGATE',
                'business_reason': 'Missing inventory snapshot data for this SKU.'
            })
            continue

        on_hand = float(inv['on_hand_units'])
        on_order = float(inv['on_order_units'])
        available_inv = on_hand + on_order
        lead_days = float(inv['lead_time_days'])
        lead_weeks = lead_days / 7.0
        lead_time_demand = avg_weekly_forecast * lead_weeks

        # 1. Stockout Risk Logic
        if lead_time_demand > 0:
            coverage = available_inv / lead_time_demand
        else:
            coverage = 999.0

        if coverage < STOCKOUT_THRESHOLDS['CRITICAL']:
            stockout_level = 'CRITICAL'
            stockout_score = 0.95
        elif coverage < STOCKOUT_THRESHOLDS['HIGH']:
            stockout_level = 'HIGH'
            stockout_score = 0.75
        elif coverage < STOCKOUT_THRESHOLDS['MEDIUM']:
            stockout_level = 'MEDIUM'
            stockout_score = 0.50
        else:
            stockout_level = 'LOW'
            stockout_score = 0.15

        # 2. Overstock Risk Logic
        if total_8w_forecast > 0:
            overstock_ratio = on_hand / total_8w_forecast
        else:
            overstock_ratio = 10.0 if on_hand > 0 else 0.0

        if overstock_ratio >= OVERSTOCK_THRESHOLDS['HIGH']:
            overstock_level = 'HIGH'
            overstock_score = 0.85
        elif overstock_ratio >= OVERSTOCK_THRESHOLDS['MEDIUM']:
            overstock_level = 'MEDIUM'
            overstock_score = 0.60
        else:
            overstock_level = 'LOW'
            overstock_score = 0.20

        # 3. Decision Matrix & Recommended Action
        is_high_stockout = stockout_level in ['CRITICAL', 'HIGH']
        is_high_overstock = overstock_level in ['HIGH']

        if is_high_stockout and not is_high_overstock:
            action = 'REORDER NOW'
            reason = f"Projected demand ({lead_time_demand:.0f} units) over {int(lead_days)}-day lead time exceeds available stock ({available_inv:.0f} units)."
        elif is_high_overstock and not is_high_stockout:
            action = 'MARKDOWN / CLEAR'
            reason = f"On-hand inventory ({on_hand:.0f} units) is {overstock_ratio:.1f}x higher than 8-week forecast demand ({total_8w_forecast:.0f} units)."
        elif is_high_stockout and is_high_overstock:
            action = 'INVESTIGATE'
            reason = f"High on-order pipeline alongside high on-hand stock indicates volatile lead times or erratic order batching."
        else:
            action = 'HEALTHY'
            reason = f"Inventory position ({available_inv:.0f} units) safely covers forecast demand ({lead_time_demand:.0f} units) without excess."

        risk_records.append({
            'sku_id': sku_id,
            'product_name': f"Product {sku_id}",
            'category': meta.get('category', 'Unknown'),
            'subcategory': meta.get('subcategory', 'Unknown'),
            'on_hand_units': int(on_hand),
            'on_order_units': int(on_order),
            'lead_time_days': int(lead_days),
            'reorder_point': int(inv.get('reorder_point', 0)),
            'forecast_8w_demand': round(total_8w_forecast, 2),
            'lead_time_demand': round(lead_time_demand, 2),
            'stockout_coverage': round(coverage, 2),
            'overstock_ratio': round(overstock_ratio, 2),
            'stockout_risk_level': stockout_level,
            'overstock_risk_level': overstock_level,
            'stockout_risk_score': stockout_score,
            'overstock_risk_score': overstock_score,
            'recommended_action': action,
            'business_reason': reason
        })

    return pd.DataFrame(risk_records)
