from pydantic import BaseModel, Field
from typing import List, Optional

class SKUPredictionRequest(BaseModel):
    sku_id: str = Field(..., example="SKU_001", description="Target SKU Identifier")
    horizon_weeks: Optional[int] = Field(default=8, ge=1, le=52, description="Forecast horizon in weeks")

class BatchPredictionRequest(BaseModel):
    sku_ids: List[str] = Field(..., example=["SKU_001", "SKU_002"], description="List of SKU Identifiers")
    horizon_weeks: Optional[int] = Field(default=8, ge=1, le=52)

class SKUPredictionResponse(BaseModel):
    sku_id: str
    product_name: str
    category: str
    subcategory: str
    on_hand_units: int
    on_order_units: int
    lead_time_days: int
    forecast_8w_demand: float
    stockout_risk_level: str
    overstock_risk_level: str
    recommended_action: str
    revenue_at_risk: float
    capital_locked: float
    business_reason: str

class BatchPredictionResponse(BaseModel):
    total_requested: int
    predictions: List[SKUPredictionResponse]

class HealthCheckResponse(BaseModel):
    status: str
    service: str
    version: str
