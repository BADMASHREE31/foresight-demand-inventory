# 🔮 FORESIGHT — Demand & Inventory Intelligence

**Client**: NorthBay Living (Direct-to-Consumer Home & Lifestyle Brand)  
**Author**: Data Scientist & Analytics Engineer (Zidio Internship Project)  
**Version**: 1.0.0 (Production-Ready)

---

## 📌 Executive Summary

NorthBay Living faced dual inventory capital losses:
1. **Stockouts**: High-demand bestsellers running out of stock leading to lost sales revenue.
2. **Overstock**: Slow-moving merchandise accumulating in warehouse storage, locking up working capital.

**FORESIGHT** turns raw transaction logs and inventory snapshots into an end-to-end demand forecasting, stockout early-warning, and working-capital risk decisioning engine.

---

## 📊 Key Calculated Results

| Metric | Calculated Value | Operational Impact |
| :--- | :--- | :--- |
| **Total Active SKUs** | **200 SKUs** | Across Furnishings, Décor, Small Appliances |
| **Seasonal-Naive Baseline WAPE** | **0.1473 (14.73%)** | Benchmark time-series error |
| **Final Selected Model (HistGB) WAPE** | **0.1192 (11.92%)** | **19.08% Accuracy Improvement** |
| **Model Selection Status** | **BEATS BASELINE** | Validated via Rolling-Origin CV |
| **Estimated Revenue at Risk** | **₹2,27,69,001.09** | Unfulfilled demand over lead time |
| **Estimated Capital Locked** | **₹1,36,54,382.76** | Excess stock tied up |
| **Immediate Reorder Candidates** | **42 SKUs** | Critical stockout coverage < 80% |
| **Healthy SKUs** | **156 SKUs** | Balanced coverage |

---

## 🏗️ System Architecture

```
foresight/
│
├── data/
│   ├── raw/                  # Ingested client extracts (CSV)
│   ├── processed/            # Cleaned, deduplicated, feature datasets
│   └── artifacts/            # Model performance JSONs & cache
│
├── src/
│   ├── config.py             # Central parameters & risk thresholds
│   ├── data_loader.py        # Ingestion & schema validator
│   ├── data_cleaning.py      # Category normalization & missing value audit
│   ├── feature_engineering.py# Prior-only lag & rolling features (Zero leakage)
│   ├── metrics.py            # WAPE, MAE, RMSE, Bias math
│   ├── baseline.py           # Seasonal-Naive Predictor
│   ├── forecasting.py        # HistGB / RF / LightGBM estimators
│   ├── backtesting.py        # Rolling-origin cross-validation engine
│   ├── risk_scoring.py       # Stockout & overstock risk score engine
│   ├── business_impact.py    # Rupee revenue at risk & capital locked
│   └── utils.py              # Dynamic natural-language explanation generator
│
├── app/                      # Streamlit Planning Dashboard
│   ├── app.py                # Main entry point & custom CSS
│   └── pages/
│       ├── 01_Executive_Overview.py
│       ├── 02_Demand_Forecast.py
│       ├── 03_Inventory_Risk.py (Includes 2D Decision Grid)
│       ├── 04_SKU_Explorer.py    (Includes "Why is this SKU classified this way?")
│       ├── 05_Business_Impact.py
│       ├── 06_Data_Quality.py
│       └── 07_Model_Performance.py
│
├── service/                  # FastAPI Scoring Microservice
│   ├── main.py               # REST API App (/health, /predict, /sku/{id})
│   ├── schemas.py            # Pydantic validation models
│   └── predictor.py          # Fast cached scoring engine
│
├── tests/                    # Automated Pytest Suite (100% Pass)
│   ├── test_pipeline.py
│   ├── test_forecasting.py
│   └── test_risk_scoring.py
│
├── generate_raw_data.py      # Reproducible raw extract generator
├── run_pipeline.py           # End-to-end 1-command pipeline runner
├── requirements.txt
└── README.md
```

---

## ⚡ Quick Start & How to Run

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Data Pipeline (1-Command Execution)
```bash
python run_pipeline.py
```

### 3. Launch Streamlit Planning Dashboard
```bash
streamlit run app/app.py
```

### 4. Launch FastAPI Scoring Microservice
```bash
uvicorn service.main:app --reload --port 8000
```
Interactive API docs available at: `http://localhost:8000/docs`

### 5. Run Automated Tests
```bash
python -m pytest tests/
```

---

## 🎯 Rolling-Origin Backtesting & Model Selection

To prevent data leakage, evaluation uses **rolling-origin cross-validation** across 4 sliding historical windows.

### Model Evaluation Summary Table

| Model | WAPE | MAE | RMSE | Bias | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Seasonal-Naive Baseline** | 0.1473 | 8.2034 | 11.0983 | -0.0215 | Benchmark |
| **HistGradientBoosting** | **0.1192** | **6.6572** | **9.1674** | **+0.1508** | **SELECTED (BEATS BASELINE)** |
| **RandomForest** | 0.1216 | 6.7867 | 9.2496 | +0.5657 | Candidate |

---

## 🛡️ Non-Negotiable Professional DS Rules Followed

1. **No Data Leakage**: All features (lags 1–52, rolling stats 4–12) use strictly prior time steps (`shift(1)` applied before rolling window computation).
2. **Time-Series Split**: Rolling-origin cross-validation employed instead of random splits.
3. **Honest Baseline Comparison**: Advanced model earned its place by outperforming Seasonal-Naive by 19.08%.
4. **Transparent Risk Logic**: Transparent, rule-based 2D decision matrix (`REORDER NOW`, `MARKDOWN / CLEAR`, `INVESTIGATE`, `HEALTHY`) avoiding black-box opacity.
