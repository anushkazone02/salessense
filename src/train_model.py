"""Train on all eligible Favorita rows. Run: python -m src.train_model."""
from time import perf_counter
from uuid import uuid4
import json
from pyspark import StorageLevel
from pyspark.ml import PipelineModel
from pyspark.ml.regression import LinearRegression, DecisionTreeRegressor, RandomForestRegressor, GBTRegressor
from pyspark.sql import Window, functions as F
from src.features import DATA, ROOT, LAGS, VALID_START, TEST_START, prepare, assembler
from src.spark_session import get_spark_session


def evaluate(frame, prediction):
    err = F.col("sales")-prediction
    n, mse, mae, variance, mean = frame.agg(F.count("*"), F.avg(err*err), F.avg(F.abs(err)),
                                             F.var_pop("sales"), F.avg("sales")).first()
    return dict(rows=n, rmse=mse**.5, mae=mae, r2=1-mse/variance, wape=mae/mean)


def train(spark):
    daily=spark.read.csv(str(DATA/"train.csv"),header=True,schema=
        "id int,date date,store_nbr int,family string,sales double,onpromotion int")
    stores=spark.read.csv(str(DATA/"stores.csv"),header=True,inferSchema=True)
    joined=daily.join(F.broadcast(stores),"store_nbr")
    # Calendar windows keep an absent date distinct from a genuine zero-sales day.
    window=Window.partitionBy("store_nbr","family").orderBy(F.datediff("date",F.lit("1970-01-01")))
    derived={f"lag{n}":F.first("sales").over(window.rangeBetween(-n,-n)) for n in LAGS}
    derived.update(prior_promo=F.first("onpromotion").over(window.rangeBetween(-7,-7)),
                   mean7=F.avg("sales").over(window.rangeBetween(-7,-1)),
                   mean28=F.avg("sales").over(window.rangeBetween(-28,-1)))
    transform=assembler()
    rows=transform.transform(prepare(joined.withColumns(derived))).select(
        "date","store_nbr","family","sales","lag7","features").persist(StorageLevel.DISK_ONLY)
    fit=rows.where(F.col("date")<VALID_START)
    validation=rows.where((F.col("date")>=VALID_START)&(F.col("date")<TEST_START))
    test=rows.where(F.col("date")>=TEST_START)
    total=rows.count(); train_rows=fit.count()
    print("Rows joined:",total,"Training:",train_rows,flush=True)
    opts=dict(featuresCol="features",labelCol="sales")
    candidates=[("Linear regression",LinearRegression(**opts,regParam=.1,maxIter=40)),
                ("Decision tree",DecisionTreeRegressor(**opts,seed=42,maxDepth=7)),
                ("Random forest",RandomForestRegressor(**opts,seed=42,maxDepth=7,numTrees=12)),
                ("Gradient-boosted trees",GBTRegressor(**opts,seed=42,maxDepth=5,maxIter=12))]
    scores=[]; best_rmse=float("inf")
    output=F.greatest(F.col("prediction"),F.lit(0.))
    for name,estimator in candidates:
        start=perf_counter(); model=estimator.fit(fit); elapsed=perf_counter()-start
        score=dict(model=name,fit_seconds=round(elapsed,2),**evaluate(model.transform(validation),output))
        print("Validation",score,flush=True); scores.append(score)
        if score["rmse"]<best_rmse:
            best,best_rmse=model,score["rmse"]
    scores.sort(key=lambda s:s["rmse"])
    scored=best.transform(test).withColumn("pred",output).cache()
    matched=scored.where(F.col("lag7")>=0)
    stats=dict(winner=scores[0]["model"],candidates=scores,total_rows=total,train_rows=train_rows,
               validation_rows=scores[0]["rows"],test=evaluate(scored,F.col("pred")),
               baseline=evaluate(matched,F.col("lag7")),matched_winner=evaluate(matched,F.col("pred")))
    run=uuid4().hex[:10]; directory=ROOT/"model"/"runs"/run; directory.mkdir(parents=True)
    PipelineModel(stages=[transform,best]).write().save(str(directory/"pipeline"))
    scored.orderBy(F.xxhash64("store_nbr","family","date"),"date","store_nbr","family").limit(400).select(
        "store_nbr","family","date","sales","pred").toPandas().to_csv(directory/"sample.csv",index=False)
    analytics={}
    for key,col in [("cities","city"),("families","family"),("weekdays","weekday"),("promotion","promoted")]:
        agg=joined.withColumns({"weekday":F.weekday("date"),"promoted":(F.col("onpromotion")>0).cast("int")}).groupBy(col).agg(
            F.count("*").alias("days"),F.sum("sales").alias("units"),F.avg("sales").alias("average"))
        analytics[key]=[r.asDict() for r in agg.orderBy(F.desc("units")).collect()]
    (directory/"analytics.json").write_text(json.dumps(analytics))
    (directory/"metrics.json").write_text(json.dumps(stats,indent=2,allow_nan=False))
    pointer=directory/"active.tmp";pointer.write_text(run);pointer.replace(ROOT/"model"/"active.txt")
    print("Final",json.dumps(stats),flush=True)


if __name__=="__main__":
    spark=get_spark_session("SalesSense-Favorita")
    try:
        train(spark)
    finally:
        spark.stop()
