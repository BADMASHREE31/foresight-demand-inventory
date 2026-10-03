import os
import pandas as pd
from src.config import PROCESSED_DATA_DIR

class ScoringEngine:
    """
    Scoring predictor engine for FastAPI service.
    Loads cached risk & forecast matrix to serve ultra-fast REST queries.
    """
    def __init__(self):
        self.risk_file = os.path.join(PROCESSED_DATA_DIR, 'risk_impact_matrix.csv')
        self._df_risk = None
        self._load()

    def _load(self):
        if os.path.exists(self.risk_file):
            self._df_risk = pd.read_csv(self.risk_file)
        else:
            self._df_risk = pd.DataFrame()

    def get_prediction(self, sku_id: str):
        if self._df_risk.empty:
            self._load()

        row = self._df_risk[self._df_risk['sku_id'] == sku_id]
        if row.empty:
            return None

        rec = row.iloc[0].to_dict()
        return {
            'sku_id': rec['sku_id'],
            'product_name': rec.get('product_name', f"Product {rec['sku_id']}"),
            'category': rec.get('category', 'Unknown'),
            'subcategory': rec.get('subcategory', 'Unknown'),
            'on_hand_units': int(rec.get('on_hand_units', 0)),
            'on_order_units': int(rec.get('on_order_units', 0)),
            'lead_time_days': int(rec.get('lead_time_days', 14)),
            'forecast_8w_demand': float(rec.get('forecast_8w_demand', 0.0)),
            'stockout_risk_level': str(rec.get('stockout_risk_level', 'LOW')),
            'overstock_risk_level': str(rec.get('overstock_risk_level', 'LOW')),
            'recommended_action': str(rec.get('recommended_action', 'HEALTHY')),
            'revenue_at_risk': float(rec.get('revenue_at_risk', 0.0)),
            'capital_locked': float(rec.get('capital_locked', 0.0)),
            'business_reason': str(rec.get('business_reason', 'Normal monitoring.'))
        }

predictor_instance = ScoringEngine()
