"""
feature_engineering.py
------------------------
Adds derived features to the cleaned Spark DataFrame and builds the
Spark ML feature-transformation Pipeline stages (StringIndexer ->
OneHotEncoder -> VectorAssembler -> StandardScaler).

This is where "raw columns" become a single numeric feature vector that
Spark MLlib's LinearRegression can consume.
"""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.ml import Pipeline
from pyspark.ml.feature import StringIndexer, OneHotEncoder, VectorAssembler, StandardScaler

from src.config import NUMERIC_FEATURES, CATEGORICAL_FEATURES


def add_date_features(df: DataFrame) -> DataFrame:
    """
    Extract Month and Day-of-week from the parsed order date.
    These capture seasonality (e.g. holiday-season sales spikes) and
    weekly patterns without needing the raw date itself as a feature
    (a raw date/timestamp isn't usable directly by LinearRegression).
    """
    df = df.withColumn("Order_Month", F.month(F.col("Order_Date_Parsed")))
    df = df.withColumn("Order_DayOfWeek", F.dayofweek(F.col("Order_Date_Parsed")))
    df = df.withColumn("Order_Year", F.year(F.col("Order_Date_Parsed")))
    return df


def build_feature_pipeline_stages():
    """
    Build the list of Spark ML Pipeline stages that turn raw categorical
    and numeric columns into a single scaled feature vector:

        For each categorical column:
            StringIndexer   (string label -> numeric index)
            OneHotEncoder   (numeric index -> sparse one-hot vector)

        VectorAssembler:    combine all numeric + one-hot columns into one vector
        StandardScaler:     standardize the assembled vector (zero mean, unit variance)

    Using a Pipeline means every one of these steps is fit ONCE on the
    training data and then applied identically (and consistently) to the
    test set and to any new/unseen data at prediction time - this is
    exactly what prevents train/test leakage and keeps the single-record
    and batch-prediction pages in the app consistent with training.
    """
    stages = []
    ohe_output_cols = []

    for cat_col in CATEGORICAL_FEATURES:
        indexed_col = f"{cat_col}_Index"
        encoded_col = f"{cat_col}_OHE"

        indexer = StringIndexer(
            inputCol=cat_col,
            outputCol=indexed_col,
            handleInvalid="keep",  # unseen categories at inference time -> extra "unknown" bucket, no crash
        )
        encoder = OneHotEncoder(inputCol=indexed_col, outputCol=encoded_col)

        stages.append(indexer)
        stages.append(encoder)
        ohe_output_cols.append(encoded_col)

    assembler_inputs = NUMERIC_FEATURES + ohe_output_cols
    assembler = VectorAssembler(
        inputCols=assembler_inputs,
        outputCol="features_raw",
        handleInvalid="skip",
    )
    stages.append(assembler)

    scaler = StandardScaler(
        inputCol="features_raw",
        outputCol="features",
        withMean=True,
        withStd=True,
    )
    stages.append(scaler)

    return stages


def build_preprocessing_pipeline() -> Pipeline:
    """Return an (unfit) Spark ML Pipeline of just the feature-engineering stages."""
    return Pipeline(stages=build_feature_pipeline_stages())
