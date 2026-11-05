"""Shared, date-relative features for one-day-ahead store-family forecasting."""
from pathlib import Path
from pyspark.ml.feature import VectorAssembler
from pyspark.sql import functions as F

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
LAGS = (1, 7, 14, 21, 28)
VALID_START = "2017-05-01"
TEST_START = "2017-07-01"


def prepare(frame):
    frame = frame.withColumns({
        "weekday": F.weekday("date"), "month": F.month("date"), "month_day": F.dayofmonth("date"),
        "promotion_change": F.col("onpromotion") - F.coalesce(F.col("prior_promo"), F.lit(0)),
        **{f"format_{t}": (F.col("type") == t).cast("int") for t in "ABCD"},
    })
    return frame.fillna(-1, subset=[f"lag{n}" for n in LAGS] + ["mean7", "mean28"])


def assembler():
    return VectorAssembler(inputCols=["weekday", "month", "month_day", "onpromotion", "promotion_change",
        "mean7", "mean28", *[f"lag{n}" for n in LAGS], *[f"format_{t}" for t in "ABCD"]],outputCol="features")
