"""
spark_session.py
------------------
Single place that creates (or reuses) the SparkSession for the whole
project. Centralizing this avoids every script spinning up its own
Spark context with different settings.
"""

import os
import shutil
import sys

from pyspark.sql import SparkSession


def _ensure_windows_hadoop_env() -> None:
    """Set the Hadoop env expected by Spark on Windows so file-based ML metadata loads correctly."""
    if os.name != "nt":
        return

    hadoop_home = os.environ.get("HADOOP_HOME") or r"C:\hadoop"
    hadoop_bin = os.path.join(hadoop_home, "bin")
    os.environ["HADOOP_HOME"] = hadoop_home

    if os.path.isdir(hadoop_bin):
        path_entries = os.environ.get("PATH", "").split(os.pathsep)
        if hadoop_bin not in path_entries:
            os.environ["PATH"] = hadoop_bin + os.pathsep + os.environ.get("PATH", "")


def _get_python_executable() -> str:
    """Return the actual interpreter used by this project and ensure Spark uses it."""
    candidates = [
        os.environ.get("PYSPARK_PYTHON"),
        os.environ.get("PYSPARK_DRIVER_PYTHON"),
        os.environ.get("PYTHON"),
        shutil.which("python"),
        shutil.which("python3"),
        sys.executable,
    ]

    for candidate in candidates:
        if candidate and os.path.exists(candidate):
            return candidate

    return sys.executable or "python"


def get_spark_session(app_name: str = "SalesSense"):
    """
    Create or reuse a local SparkSession.

    Uses local[*] so Spark uses all available CPU cores on this machine,
    which is what demonstrates parallel/distributed-style processing on
    a single machine for a college project (in a real deployment this
    same code would run unchanged on a cluster by changing the master URL).
    """
    _ensure_windows_hadoop_env()

    python_executable = _get_python_executable()
    os.environ.setdefault("PYSPARK_PYTHON", python_executable)
    os.environ.setdefault("PYSPARK_DRIVER_PYTHON", python_executable)

    spark = (
        SparkSession.builder.appName(app_name)
        .master("local[*]")
        .config("spark.sql.shuffle.partitions", "8")  # small dataset -> fewer shuffle partitions than the 200 default
        .config("spark.driver.memory", "2g")
        .config("spark.ui.showConsoleProgress", "false")
        .config("spark.pyspark.python", python_executable)
        .config("spark.pyspark.driver.python", python_executable)
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("ERROR")  # keep console output readable
    return spark
