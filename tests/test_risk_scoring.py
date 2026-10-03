import pytest
import pandas as pd
from src.risk_scoring import score_inventory_risks
from src.business_impact import calculate_business_impact

def test_risk_scoring_logic():
    df_fcst = pd.DataFrame({
        'sku_id': ['SKU_TEST_1'] * 8,
        'forecast': [10.0] * 8 # 80 total forecast, 10/wk
    })
    
    # Inventory: on_hand = 5, on_order = 0, lead_time = 14 days (2 weeks).
    # Lead time demand = 20 units. Available = 5 units. Coverage = 5/20 = 0.25 (CRITICAL)
    df_inv = pd.DataFrame({
        'sku_id': ['SKU_TEST_1'],
        'on_hand_units': [5],
        'on_order_units': [0],
        'lead_time_days': [14],
        'reorder_point': [25]
    })
    
    df_sku = pd.DataFrame({
        'sku_id': ['SKU_TEST_1'],
        'category': ['Furnishings'],
        'subcategory': ['Bedding'],
        'unit_cost': [100.0],
        'list_price': [200.0]
    })
    
    risk_df = score_inventory_risks(df_fcst, df_inv, df_sku)
    assert len(risk_df) == 1
    assert risk_df.iloc[0]['recommended_action'] == 'REORDER NOW'
    
    impact_df, summary = calculate_business_impact(risk_df, df_sku)
    # Unfulfilled units = 20 - 5 = 15 units. Revenue at risk = 15 * 200 = 3000
    assert pytest.approx(impact_df.iloc[0]['revenue_at_risk'], 0.1) == 3000.0
