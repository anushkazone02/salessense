"""
preprocessing.py
------------------
Loads the raw Superstore CSV into a Spark DataFrame and performs data
cleaning: column renaming, type casting, null/duplicate handling, and
basic sanity filtering.

This is the "Data Cleaning" stage of the pipeline:
    Dataset -> Data Cleaning -> Feature Engineering -> ...
"""

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType, IntegerType

from src.config import RAW_DATA_PATH, COLUMN_RENAME_MAP


def load_raw_data(spark: SparkSession, path: str = RAW_DATA_PATH) -> DataFrame:
    """
    Read the raw CSV into a Spark DataFrame using Spark's distributed
    CSV reader (schema inference happens across the whole file, not
    just a preview, and the read is parallelized across partitions).
    """
    df = (
        spark.read.option("header", True)
        .option("inferSchema", True)
        .option("encoding", "ISO-8859-1")  # dataset contains some non-UTF8 characters
        .option("quote", '"')
        .option("escape", '"')  # CSV uses doubled "" to escape a literal quote inside a quoted field
        .option("multiLine", True)  # some product names contain embedded newlines/commas
        .csv(path)
    )
    return df


def rename_columns(df: DataFrame) -> DataFrame:
    """Rename raw CSV headers (which contain spaces/hyphens) to Spark-safe identifiers."""
    for old_name, new_name in COLUMN_RENAME_MAP.items():
        if old_name in df.columns:
            df = df.withColumnRenamed(old_name, new_name)
    return df


def clean_data(df: DataFrame) -> DataFrame:
    """
    Core cleaning steps:
      1. Drop exact duplicate rows.
      2. Drop rows with nulls in columns that are essential for training.
      3. Cast numeric columns to proper types.
      4. Filter out logically invalid rows (e.g. non-positive Sales/Quantity).
      5. Parse Order_Date into a real date type.
    """
    essential_cols = [
        "Sales", "Quantity", "Discount", "Category", "Sub_Category",
        "Segment", "Region", "Ship_Mode", "Order_Date",
    ]

    before_count = df.count()

    # 1. Drop exact duplicates
    df = df.dropDuplicates()

    # 2. Drop rows missing any essential column
    df = df.dropna(subset=essential_cols)

    # 3. Cast numeric columns explicitly (defensive, even if inferSchema got it right)
    df = (
        df.withColumn("Sales", F.col("Sales").cast(DoubleType()))
        .withColumn("Quantity", F.col("Quantity").cast(IntegerType()))
        .withColumn("Discount", F.col("Discount").cast(DoubleType()))
    )

    # 4. Filter logically invalid rows
    df = df.filter((F.col("Sales") > 0) & (F.col("Quantity") > 0) & (F.col("Discount") >= 0))

    # 5. Parse Order_Date (format in raw file is M/d/yyyy, e.g. 11/8/2016)
    df = df.withColumn("Order_Date_Parsed", F.to_date(F.col("Order_Date"), "M/d/yyyy"))
    df = df.dropna(subset=["Order_Date_Parsed"])

    after_count = df.count()
    print(f"[preprocessing] Rows before cleaning: {before_count} | after cleaning: {after_count} "
          f"| removed: {before_count - after_count}")

    return df


def get_clean_dataframe(spark: SparkSession, path: str = RAW_DATA_PATH) -> DataFrame:
    """Convenience wrapper: load raw data, rename columns, and clean it."""
    df = load_raw_data(spark, path)
    df = rename_columns(df)
    df = clean_data(df)
    return df


if __name__ == "__main__":
    # Quick standalone check: run `python -m src.preprocessing` from project root
    from src.spark_session import get_spark_session

    spark = get_spark_session()
    clean_df = get_clean_dataframe(spark)
    clean_df.printSchema()
    clean_df.show(5, truncate=False)
    spark.stop()
