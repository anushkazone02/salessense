"""
prediction.py
----------------
Loads the saved Spark PipelineModel and exposes simple functions the
Streamlit app uses for:
  - single-record prediction (from form inputs)
  - batch prediction (from an uploaded CSV)

Keeping this separate from the Streamlit UI code means the prediction
logic can be tested/reused independently of the GUI.
"""

import pandas as pd
from pyspark.ml import PipelineModel
from pyspark.sql import SparkSession
from pyspark.sql.types import (
    StructType, StructField, StringType, IntegerType, DoubleType
)

from src.config import TRAINED_MODEL_PATH


INPUT_SCHEMA = StructType([
    StructField("Category", StringType(), True),
    StructField("Sub_Category", StringType(), True),
    StructField("Segment", StringType(), True),
    StructField("Region", StringType(), True),
    StructField("Ship_Mode", StringType(), True),
    StructField("Quantity", IntegerType(), True),
    StructField("Discount", DoubleType(), True),
    StructField("Order_Month", IntegerType(), True),
    StructField("Order_DayOfWeek", IntegerType(), True),
])


def load_model(spark: SparkSession) -> PipelineModel:
    """Load the trained PipelineModel saved by src/train_model.py."""
    return PipelineModel.load(TRAINED_MODEL_PATH)


def predict_single(spark: SparkSession, model: PipelineModel, record: dict) -> float:
    """
    Run a single prediction.

    `record` should be a dict with keys matching INPUT_SCHEMA field names.
    Returns the predicted Sales value as a Python float.
    """
    row = [(
        record["Category"],
        record["Sub_Category"],
        record["Segment"],
        record["Region"],
        record["Ship_Mode"],
        int(record["Quantity"]),
        float(record["Discount"]),
        int(record["Order_Month"]),
        int(record["Order_DayOfWeek"]),
    )]
    input_df = spark.createDataFrame(row, schema=INPUT_SCHEMA)
    result = model.transform(input_df)
    prediction = result.select("prediction").first()["prediction"]
    return max(float(prediction), 0.0)  # sales can't be negative; clip defensively


def predict_batch(spark: SparkSession, model: PipelineModel, input_pandas_df: pd.DataFrame) -> pd.DataFrame:
    """
    Run batch prediction on an uploaded CSV (already read into a pandas DataFrame).

    Expects columns: Category, Sub_Category, Segment, Region, Ship_Mode,
    Quantity, Discount, Order_Month, Order_DayOfWeek
    (Order_Month / Order_DayOfWeek may instead be derived from an Order_Date
    column by the caller before this is invoked.)

    Returns the original pandas DataFrame with a new 'Predicted_Sales' column.
    """
    required_cols = [f.name for f in INPUT_SCHEMA.fields]
    missing = [c for c in required_cols if c not in input_pandas_df.columns]
    if missing:
        raise ValueError(
            f"Uploaded file is missing required columns: {missing}. "
            f"Expected columns: {required_cols}"
        )

    # Coerce dtypes defensively so Spark doesn't choke on strings-that-look-like-numbers
    work_df = input_pandas_df.copy()
    work_df["Quantity"] = pd.to_numeric(work_df["Quantity"], errors="coerce").fillna(1).astype(int)
    work_df["Discount"] = pd.to_numeric(work_df["Discount"], errors="coerce").fillna(0.0).astype(float)
    work_df["Order_Month"] = pd.to_numeric(work_df["Order_Month"], errors="coerce").fillna(1).astype(int)
    work_df["Order_DayOfWeek"] = pd.to_numeric(work_df["Order_DayOfWeek"], errors="coerce").fillna(1).astype(int)

    spark_df = spark.createDataFrame(work_df[required_cols], schema=INPUT_SCHEMA)
    result = model.transform(spark_df)
    predictions_pd = result.select("prediction").toPandas()

    output_df = input_pandas_df.copy().reset_index(drop=True)
    output_df["Predicted_Sales"] = predictions_pd["prediction"].clip(lower=0).round(2)
    return output_df
