"""
analytics.py
--------------
Spark-based aggregation helpers for the Dashboard and Analytics pages.

Aggregations (group-by, sum, avg) are computed IN SPARK on the cleaned
DataFrame -- this is the "distributed data processing" demonstration
required by the project brief -- and only the small, already-aggregated
result is converted to pandas for Plotly charting in Streamlit.
"""

import pandas as pd
from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def get_summary_kpis(df: DataFrame) -> dict:
    """Total sales, average sale, transaction count, best category — computed in Spark."""
    agg = df.agg(
        F.sum("Sales").alias("total_sales"),
        F.avg("Sales").alias("avg_sales"),
        F.count("*").alias("num_transactions"),
        F.sum("Profit").alias("total_profit"),
    ).first()

    best_category_row = (
        df.groupBy("Category")
        .agg(F.sum("Sales").alias("category_sales"))
        .orderBy(F.desc("category_sales"))
        .first()
    )

    return {
        "total_sales": float(agg["total_sales"]),
        "avg_sales": float(agg["avg_sales"]),
        "num_transactions": int(agg["num_transactions"]),
        "total_profit": float(agg["total_profit"]),
        "best_category": best_category_row["Category"],
        "best_category_sales": float(best_category_row["category_sales"]),
    }


def sales_by_month(df: DataFrame) -> pd.DataFrame:
    """Monthly sales trend (year-month), computed via Spark groupBy."""
    result = (
        df.withColumn("YearMonth", F.date_format(F.col("Order_Date_Parsed"), "yyyy-MM"))
        .groupBy("YearMonth")
        .agg(F.sum("Sales").alias("Total_Sales"), F.count("*").alias("Num_Orders"))
        .orderBy("YearMonth")
    )
    return result.toPandas()


def sales_by_weekday(df: DataFrame) -> pd.DataFrame:
    """Sales aggregated by day of week."""
    result = (
        df.withColumn("Weekday", F.date_format(F.col("Order_Date_Parsed"), "EEEE"))
        .groupBy("Weekday")
        .agg(F.sum("Sales").alias("Total_Sales"), F.count("*").alias("Num_Orders"))
    )
    return result.toPandas()


def sales_by_category(df: DataFrame) -> pd.DataFrame:
    result = (
        df.groupBy("Category")
        .agg(F.sum("Sales").alias("Total_Sales"), F.count("*").alias("Num_Orders"),
             F.avg("Sales").alias("Avg_Sales"))
        .orderBy(F.desc("Total_Sales"))
    )
    return result.toPandas()


def sales_by_subcategory(df: DataFrame) -> pd.DataFrame:
    result = (
        df.groupBy("Sub_Category")
        .agg(F.sum("Sales").alias("Total_Sales"), F.count("*").alias("Num_Orders"))
        .orderBy(F.desc("Total_Sales"))
    )
    return result.toPandas()


def sales_by_region(df: DataFrame) -> pd.DataFrame:
    result = (
        df.groupBy("Region")
        .agg(F.sum("Sales").alias("Total_Sales"), F.count("*").alias("Num_Orders"))
        .orderBy(F.desc("Total_Sales"))
    )
    return result.toPandas()


def sales_by_segment(df: DataFrame) -> pd.DataFrame:
    result = (
        df.groupBy("Segment")
        .agg(F.sum("Sales").alias("Total_Sales"), F.count("*").alias("Num_Orders"))
        .orderBy(F.desc("Total_Sales"))
    )
    return result.toPandas()


def top_products(df: DataFrame, n: int = 10) -> pd.DataFrame:
    result = (
        df.groupBy("Product_Name")
        .agg(F.sum("Sales").alias("Total_Sales"), F.count("*").alias("Num_Orders"))
        .orderBy(F.desc("Total_Sales"))
        .limit(n)
    )
    return result.toPandas()


def discount_vs_sales_sample(df: DataFrame, n: int = 2000) -> pd.DataFrame:
    """A sample of raw rows for the Discount vs Sales scatter plot."""
    return df.select("Discount", "Sales", "Quantity", "Category").limit(n).toPandas()


def get_raw_pandas_for_filters(df: DataFrame) -> pd.DataFrame:
    """
    Convert the full cleaned dataset to pandas ONCE, for interactive
    client-side filtering in the Dashboard/Analytics pages (date range,
    category, region filters applied via pandas/Streamlit widgets rather
    than re-querying Spark on every widget interaction).
    """
    cols = [
        "Order_Date_Parsed", "Category", "Sub_Category", "Segment", "Region",
        "Ship_Mode", "State", "City", "Sales", "Quantity", "Discount", "Profit",
        "Product_Name",
    ]
    pdf = df.select(cols).toPandas()
    # Spark's DateType can come back as python `datetime.date` objects (object
    # dtype) rather than pandas datetime64 depending on the Arrow/pandas
    # version in use, which breaks Timestamp comparisons in the UI filters.
    # Force a proper datetime64 dtype here so downstream code can rely on it.
    pdf["Order_Date_Parsed"] = pd.to_datetime(pdf["Order_Date_Parsed"])
    return pdf
