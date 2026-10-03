# Project FORESIGHT — Executive Presentation Readout
**Client**: NorthBay Living  
**Audience**: Head of Operations, Merchandising Lead, Finance Lead  

---

### Slide 1: Title Slide
# 🔮 FORESIGHT
### Demand & Inventory Intelligence Suite
**Transforming Sales History into Actionable Inventory Working-Capital Decisions**  
*Client Engagement Final Readout | NorthBay Living*

---

### Slide 2: Business Problem
## The Challenge at NorthBay Living
* **Dual Financial Drainage**: Best-sellers frequently stock out (lost sales revenue), while slow movers accumulate in storage (locked working capital).
* **Spreadsheet Dependence**: Operations relies on gut-feel ordering without systematic lead-time demand forecasting.
* **Goal**: Deliver a reliable SKU-level forecast, automated stockout/overstock early-warning flags, and quantifiable Rupee revenue-at-risk calculations.

---

### Slide 3: Data & Solution Architecture
## Data Foundation & Reproducible Pipeline
* **Ingested Extracts**: `sales_daily`, `sku_master`, `calendar`, `inventory_snapshots` (200 SKUs, ~2 years daily transactions).
* **Data Quality**: 99.91% completeness; automated category normalization, deduplication, and missing value imputation.
* **Leakage-Free Features**: All lag (1-52 wks) and rolling window features engineered strictly from prior time periods.

---

### Slide 4: Demand Forecast Performance
## Honest Backtest & Baseline Comparison
* **Primary Metric**: Weighted Absolute Percentage Error (WAPE).
* **Validation Method**: 4-Window Rolling-Origin Cross-Validation (No random splits).
* **Results**:
  * **Seasonal-Naive Baseline WAPE**: **14.73%**
  * **HistGradientBoosting Model WAPE**: **11.92%**
  * **Outcome**: **BEATS BASELINE BY 19.08%** — HistGradientBoosting deployed for production forecasts.

---

### Slide 5: Stockout / Overstock Risk Logic
## Transparent 2D Decision Matrix
* **Stockout Risk**: Compares 14-day lead-time forecast demand against available stock (`on_hand + on_order`).
* **Overstock Risk**: Compares on-hand inventory against 8-week forward forecast demand.
* **Four Action Quadrants**:
  1. **REORDER NOW** (High Stockout, Low Overstock)
  2. **MARKDOWN / CLEAR** (High Overstock, Low Stockout)
  3. **INVESTIGATE** (High Stockout, High Overstock — Volatile Lead Time)
  4. **HEALTHY** (Balanced Inventory Position)

---

### Slide 6: Quantified Financial Impact
## Rupee Value at Stake
* **Total Estimated Revenue at Risk (Stockouts)**: **₹2,27,69,001.09**
* **Total Estimated Capital Locked (Excess Stock)**: **₹1,36,54,382.76**
* **Immediate Reorder Candidates**: **42 SKUs** requiring urgent purchase order placement.

---

### Slide 7: Priority Recommended Actions
## Top Operational Next Steps
1. **Immediate Purchase Orders**: Place replenishment orders for the 42 **REORDER NOW** SKUs to protect ₹2.27 Cr in potential lost revenue.
2. **Category Review**: Prioritize Small Appliances & Furnishings replenishment schedules.
3. **Supplier Lead Time Alignment**: Conduct supplier review for items in the **INVESTIGATE** quadrant to stabilize pipeline delivery times.

---

### Slide 8: Interactive Dashboard & API Overview
## Operations Self-Service Tools
* **Streamlit Planning Dashboard**:
  * Executive Overview KPI Cards
  * Interactive Demand Forecasting with 80% Confidence Intervals
  * 2D Interactive Decisioning Grid
  * SKU Explorer with Dynamic Natural Language Explanations
* **FastAPI Scoring Microservice**: Real-time REST endpoints (`GET /sku/{id}`, `POST /predict`) for ERP integration.

---

### Slide 9: Assumptions & Limitations
## Transparency & Governance
* **Assumptions**: Current supplier lead times and reorder points in inventory extracts are broadly reflective of operational realities.
* **Limitations**: High-volatility promotional spikes can widen 80% forecast uncertainty bounds. New SKU launches rely on category-level average initialization.

---

### Slide 10: Next Steps & Handover
## Roadmap
* **Week 1-2**: Operations team onboarding on Streamlit Planning Dashboard.
* **Week 3-4**: ERP integration via FastAPI scoring endpoints.
* **Ongoing**: Quarterly rolling-origin backtest re-tuning.
