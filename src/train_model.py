"""
train_model.py
-----------------
Full training script for SalesSense.

Pipeline:
    Load raw CSV (Spark)
    -> Clean data
    -> Feature engineering (date parts)
    -> Train/test split
    -> Fit Spark ML Pipeline (indexers + encoders + assembler + scaler + LinearRegression)
    -> Evaluate on the held-out test set (RMSE, MAE, R2)
    -> Save the fitted PipelineModel to disk (used later by the Streamlit app)
    -> Save metrics + a sample of predictions for the "Model Performance" page

Run with:  python -m src.train_model   (from the project root)
"""

import json
import time

from pyspark.ml import Pipeline
from pyspark.ml.regression import LinearRegression
from pyspark.ml.evaluation import RegressionEvaluator

from src.config import (
    RANDOM_SEED, TRAIN_RATIO, TEST_RATIO, TARGET_COLUMN,
    TRAINED_MODEL_PATH, METRICS_PATH, PREDICTIONS_SAMPLE_PATH,
)
from src.spark_session import get_spark_session
from src.preprocessing import get_clean_dataframe
from src.feature_engineering import add_date_features, build_feature_pipeline_stages


def train_and_evaluate():
    spark = get_spark_session()

    print("=" * 70)
    print("STAGE: Loading and cleaning data with Spark")
    print("=" * 70)
    df = get_clean_dataframe(spark)
    df = add_date_features(df)
    df = df.cache()  # reused across split + multiple transforms below
    total_rows = df.count()
    print(f"Total clean rows available for modeling: {total_rows}")

    print("\n" + "=" * 70)
    print("STAGE: Train/Test split")
    print("=" * 70)
    train_df, test_df = df.randomSplit([TRAIN_RATIO, TEST_RATIO], seed=RANDOM_SEED)
    train_df = train_df.cache()
    test_df = test_df.cache()
    print(f"Train rows: {train_df.count()}  |  Test rows: {test_df.count()}")

    print("\n" + "=" * 70)
    print("STAGE: Building Spark ML Pipeline (StringIndexer -> OneHotEncoder -> "
          "VectorAssembler -> StandardScaler -> LinearRegression)")
    print("=" * 70)
    feature_stages = build_feature_pipeline_stages()
    lr = LinearRegression(
        featuresCol="features",
        labelCol=TARGET_COLUMN,
        predictionCol="prediction",
        maxIter=50,
        regParam=0.1,       # small L2 regularization for stability
        elasticNetParam=0.0,
    )
    full_pipeline = Pipeline(stages=feature_stages + [lr])

    print("\n" + "=" * 70)
    print("STAGE: Fitting model on training data")
    print("=" * 70)
    start = time.time()
    pipeline_model = full_pipeline.fit(train_df)
    elapsed = time.time() - start
    print(f"Training completed in {elapsed:.2f} seconds")

    lr_model = pipeline_model.stages[-1]
    print(f"Coefficients (first 10 of {len(lr_model.coefficients)}): "
          f"{list(lr_model.coefficients)[:10]}")
    print(f"Intercept: {lr_model.intercept:.4f}")

    print("\n" + "=" * 70)
    print("STAGE: Evaluating on held-out test set")
    print("=" * 70)
    predictions = pipeline_model.transform(test_df)

    evaluator_rmse = RegressionEvaluator(labelCol=TARGET_COLUMN, predictionCol="prediction", metricName="rmse")
    evaluator_mae = RegressionEvaluator(labelCol=TARGET_COLUMN, predictionCol="prediction", metricName="mae")
    evaluator_r2 = RegressionEvaluator(labelCol=TARGET_COLUMN, predictionCol="prediction", metricName="r2")

    rmse = evaluator_rmse.evaluate(predictions)
    mae = evaluator_mae.evaluate(predictions)
    r2 = evaluator_r2.evaluate(predictions)

    # Also report training-set metrics (useful for the report / viva: shows no wild overfit)
    train_predictions = pipeline_model.transform(train_df)
    train_rmse = evaluator_rmse.evaluate(train_predictions)
    train_r2 = evaluator_r2.evaluate(train_predictions)

    print(f"TEST  RMSE : {rmse:.4f}")
    print(f"TEST  MAE  : {mae:.4f}")
    print(f"TEST  R2   : {r2:.4f}")
    print(f"TRAIN RMSE : {train_rmse:.4f}")
    print(f"TRAIN R2   : {train_r2:.4f}")

    print("\n" + "=" * 70)
    print("STAGE: Saving model and metrics")
    print("=" * 70)
    pipeline_model.write().overwrite().save(TRAINED_MODEL_PATH)
    print(f"Model saved to: {TRAINED_MODEL_PATH}")

    metrics = {
        "rmse": rmse,
        "mae": mae,
        "r2": r2,
        "train_rmse": train_rmse,
        "train_r2": train_r2,
        "train_rows": train_df.count(),
        "test_rows": test_df.count(),
        "total_rows": total_rows,
        "training_time_seconds": round(elapsed, 2),
        "feature_vector_size": int(len(lr_model.coefficients)),
        "intercept": float(lr_model.intercept),
        "random_seed": RANDOM_SEED,
    }
    with open(METRICS_PATH, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"Metrics saved to: {METRICS_PATH}")
    print(json.dumps(metrics, indent=2))

    # Save a sample of actual-vs-predicted for the Model Performance page
    sample_pd = (
        predictions.select(TARGET_COLUMN, "prediction")
        .withColumnRenamed(TARGET_COLUMN, "actual_sales")
        .withColumnRenamed("prediction", "predicted_sales")
        .limit(500)
        .toPandas()
    )
    sample_pd["residual"] = sample_pd["actual_sales"] - sample_pd["predicted_sales"]
    sample_pd.to_csv(PREDICTIONS_SAMPLE_PATH, index=False)
    print(f"Sample predictions saved to: {PREDICTIONS_SAMPLE_PATH}")

    spark.stop()
    return metrics


if __name__ == "__main__":
    train_and_evaluate()
