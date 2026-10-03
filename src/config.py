import os

# Base Directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
MODEL_ARTIFACTS_DIR = os.path.join(BASE_DIR, "data", "artifacts")

# Create required directories
for d in [RAW_DATA_DIR, PROCESSED_DATA_DIR, REPORTS_DIR, MODEL_ARTIFACTS_DIR]:
    os.makedirs(d, exist_ok=True)

# Forecasting Parameters
FORECAST_HORIZON_WEEKS = 8
DEFAULT_FREQUENCY = "W-MON"
RANDOM_SEED = 42

# Backtesting Parameters
BACKTEST_INITIAL_WEEKS = 52
BACKTEST_STEP_WEEKS = 4
BACKTEST_NUM_WINDOWS = 4

# Data Cleaning Mappings
CATEGORY_MAPPING = {
    'furnishings': 'Furnishings',
    'furnishing': 'Furnishings',
    'furnishings': 'Furnishings',
    'decor': 'Décor',
    'décor': 'Décor',
    'decor': 'Décor',
    'small appliances': 'Small Appliances',
    'small_appliances': 'Small Appliances'
}

# Risk Thresholds
# Stockout Risk: Projected inventory coverage over lead time vs demand
STOCKOUT_THRESHOLDS = {
    'CRITICAL': 0.5, # Stock covers less than 50% of lead time demand
    'HIGH': 0.8,     # Stock covers 50-80% of lead time demand
    'MEDIUM': 1.0,   # Stock covers 80-100% of lead time demand
    'LOW': 1.2       # Stock covers >120% of lead time demand
}

# Overstock Risk: Inventory / (8-week forecast demand) ratio
OVERSTOCK_THRESHOLDS = {
    'HIGH': 2.5,   # Available stock > 2.5x 8-week forecast
    'MEDIUM': 1.5, # Available stock 1.5x - 2.5x 8-week forecast
    'LOW': 1.0     # Available stock <= 1.5x 8-week forecast
}

# Safety Stock Factor
SAFETY_STOCK_FACTOR = 1.2
