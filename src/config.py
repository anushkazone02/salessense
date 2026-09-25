"""
config.py
----------
Central configuration for the SalesSense project.

Keeping paths and constants here (instead of hardcoding them in every
script) means the project can be moved to another machine or another
folder and only this file needs to change.
"""

import os

# Project root = one level above this file's directory (src/ -> project root)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Data
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
RAW_DATA_PATH = os.path.join(DATA_DIR, "superstore.csv")

# Model
MODEL_DIR = os.path.join(PROJECT_ROOT, "model")
TRAINED_MODEL_PATH = os.path.join(MODEL_DIR, "trained_model")
METRICS_PATH = os.path.join(MODEL_DIR, "metrics.json")
PREDICTIONS_SAMPLE_PATH = os.path.join(MODEL_DIR, "test_predictions_sample.csv")

# Reproducibility
RANDOM_SEED = 42

# Train/test split ratio
TRAIN_RATIO = 0.8
TEST_RATIO = 0.2

# Columns used as model inputs (features) and the prediction target.
# NOTE: 'Profit' is intentionally excluded — in this dataset Profit is
# derived from Sales, so using it as a feature would leak the target.
NUMERIC_FEATURES = ["Quantity", "Discount", "Order_Month", "Order_DayOfWeek"]
CATEGORICAL_FEATURES = ["Category", "Sub_Category", "Segment", "Region", "Ship_Mode"]
TARGET_COLUMN = "Sales"

# Raw column names in the CSV -> Spark-safe column names (no spaces/hyphens)
COLUMN_RENAME_MAP = {
    "Row ID": "Row_ID",
    "Order ID": "Order_ID",
    "Order Date": "Order_Date",
    "Ship Date": "Ship_Date",
    "Ship Mode": "Ship_Mode",
    "Customer ID": "Customer_ID",
    "Customer Name": "Customer_Name",
    "Postal Code": "Postal_Code",
    "Product ID": "Product_ID",
    "Sub-Category": "Sub_Category",
    "Product Name": "Product_Name",
}
