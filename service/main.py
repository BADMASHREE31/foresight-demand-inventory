import os
import sys
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from service.schemas import (
    SKUPredictionRequest,
    SKUPredictionResponse,
    BatchPredictionRequest,
    BatchPredictionResponse,
    HealthCheckResponse
)
from service.predictor import predictor_instance

app = FastAPI(
    title="FORESIGHT Demand & Inventory Intelligence API",
    description="Deployed scoring service returning weekly demand forecasts, stockout/overstock risk scores, and rupee impact for NorthBay Living.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", response_model=HealthCheckResponse, summary="Health Check Endpoint")
def health_check():
    return {
        "status": "healthy",
        "service": "FORESIGHT Demand & Inventory Intelligence Service",
        "version": "1.0.0"
    }

@app.get("/sku/{sku_id}", response_model=SKUPredictionResponse, summary="Get Risk & Forecast by SKU ID")
def get_sku_score(sku_id: str):
    res = predictor_instance.get_prediction(sku_id)
    if res is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SKU '{sku_id}' not found in inventory catalog."
        )
    return res

@app.post("/predict", response_model=SKUPredictionResponse, summary="Predict Risk & Forecast for Single SKU")
def predict_sku(req: SKUPredictionRequest):
    res = predictor_instance.get_prediction(req.sku_id)
    if res is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SKU '{req.sku_id}' not found in inventory catalog."
        )
    return res

@app.post("/batch_predict", response_model=BatchPredictionResponse, summary="Batch Predict Risk & Forecast")
def batch_predict(req: BatchPredictionRequest):
    predictions = []
    for s_id in req.sku_ids:
        res = predictor_instance.get_prediction(s_id)
        if res is not None:
            predictions.append(res)

    return {
        "total_requested": len(req.sku_ids),
        "predictions": predictions
    }
