"""Local Favorita store-family demand service. Run python app.py."""
from datetime import date
from functools import lru_cache
from pathlib import Path
from threading import Lock
import csv
import io
import json
import pandas as pd
import plotly
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, ValidationError
from src.history import ROOT, connect, history_features

app=FastAPI(title="SalesSense | Favorita grocery demand")
app.mount("/assets",StaticFiles(directory=ROOT/"web"),name="assets")
run=ROOT/"model/runs"/(ROOT/"model/active.txt").read_text().strip()
metrics=json.loads((run/"metrics.json").read_text())
first,last=date(2013,1,1),date(2017,8,15)
replay,next_day=date(2017,5,1),date(2017,8,16)
lock=Lock()


@app.get("/",include_in_schema=False)
def dashboard(): return FileResponse(ROOT/"web/index.html")


@app.get("/vendor/plotly.js",include_in_schema=False)
def charts(): return FileResponse(Path(plotly.__file__).parent/"package_data/plotly.min.js",media_type="text/javascript")


@app.get("/api/config")
@lru_cache(maxsize=1)
def config():
    with connect() as c:
        stores=[dict(r) for r in c.execute("SELECT store_nbr,city,state FROM stores ORDER BY city,store_nbr")]
        families=[r[0] for r in c.execute("SELECT DISTINCT family FROM plans ORDER BY family")]
    return dict(stores=stores,families=families,first=first,last=last,next=next_day,
                forecast_first=replay,winner=metrics["winner"])


def filters(city,family,start,end):
    if start and end and start>end: raise HTTPException(422,"Select an end date on or after the start date.")
    clauses=[];args=[]
    for cond,val in [("s.city=?",city),("d.family=?",family),("d.date>=?",start),("d.date<=?",end)]:
        if val:
            clauses.append(cond);args.append(str(val))
    return " FROM daily d JOIN stores s ON d.store_nbr=s.store_nbr "+("WHERE "+" AND ".join(clauses) if clauses else ""),args


@app.get("/api/overview")
@lru_cache(maxsize=32)
def overview(city:str="",family:str="",start:date=None,end:date=None):
    base,args=filters(city,family,start,end)
    with connect() as conn:
        def query(cols,suffix=""):
            return [dict(r) for r in conn.execute("SELECT "+cols+base+" "+suffix,args)]
        totals=query("COUNT(*) days, COUNT(DISTINCT d.store_nbr) stores, COUNT(DISTINCT family) families, COALESCE(SUM(sales),0) units")[0]
        months=query("substr(date,1,7)||'-01' month,SUM(sales) units,COUNT(*) records","GROUP BY month ORDER BY month")
        groups=query("family name,SUM(sales) units,COUNT(*) records,SUM(onpromotion>0) promoted","GROUP BY family ORDER BY units DESC")
    return dict(**totals,months=months,groups=groups)


@app.get("/api/overview.csv")
def export(city:str="",family:str="",start:date=None,end:date=None):
    base,args=filters(city,family,start,end)
    def chunks():
        with connect() as conn:
            cur=conn.execute("SELECT d.date,s.city,d.store_nbr,d.family,d.sales,d.onpromotion"+base,args)
            buf=io.StringIO();writer=csv.writer(buf);writer.writerow([x[0] for x in cur.description])
            while rows:=cur.fetchmany(4096):
                writer.writerows(rows);yield buf.getvalue();buf.seek(0);buf.truncate(0)
            yield buf.getvalue()
    return StreamingResponse(chunks(),media_type="text/csv",headers={"Content-Disposition":"attachment; filename=favorita-selection.csv"})


@app.get("/api/models")
def models(): return {**metrics,"sample":pd.read_csv(run/"sample.csv").to_dict("records")}


@app.get("/api/analytics")
def analytics(): return json.loads((run/"analytics.json").read_text())


class Plan(BaseModel):
    store_nbr:int=Field(ge=1)
    family:str
    date:date
    onpromotion:int=Field(ge=0,le=2147483647)


@app.get("/api/promotion")
def promotion(store_nbr:int,family:str,day:date):
    source="plans" if day>last else "daily"
    with connect() as conn:
        row=conn.execute(f"SELECT onpromotion FROM {source} WHERE store_nbr=? AND family=? AND date=?",
                         (store_nbr,family,str(day))).fetchone()
        prior=conn.execute("SELECT date,sales FROM daily WHERE store_nbr=? AND family=? AND date=date(?,'-7 days')",
                           (store_nbr,family,str(day))).fetchone()
    return {"onpromotion":row[0] if row else None,"prior_week":dict(prior) if prior else None}


@lru_cache(maxsize=1)
def runtime():
    from src.spark_session import get_spark_session
    from pyspark.ml import PipelineModel
    spark=get_spark_session("SalesSense-Favorita-API")
    return spark,PipelineModel.load(str(run/"pipeline"))


def forecasts(plans):
    from src.features import prepare,LAGS
    from pyspark.sql import functions as F
    import pyarrow as pa
    cfg=config();stores={s["store_nbr"] for s in cfg["stores"]}
    for i,p in enumerate(plans,1):
        if p.store_nbr not in stores or p.family not in cfg["families"] or not replay<=p.date<=next_day:
            raise HTTPException(422,f"Row {i}: use a listed store and family, and a date from {replay} through {next_day}.")
    df=history_features([p.model_dump() for p in plans])
    schema=("line int,store_nbr int,family string,date string,onpromotion int,type string,"
            "mean28 double,mean7 double,prior_promo double,"+",".join(f"lag{n} double" for n in LAGS))
    with lock:
        spark,model=runtime()
        inputs=spark.createDataFrame(pa.Table.from_pandas(df,preserve_index=False),schema=schema)
        results=model.transform(prepare(inputs.withColumn("date",F.to_date("date"))))
        return [float(r[0]) for r in results.orderBy("line").select(F.greatest("prediction",F.lit(0.))).collect()]


@app.post("/api/predict")
def predict(plan:Plan): return dict(units=forecasts([plan])[0],model=metrics["winner"])


def download(df,name):
    return Response(df.to_csv(index=False),media_type="text/csv",headers={"Content-Disposition":f'attachment; filename="{name}"'})


@app.get("/api/template.csv")
def template():
    with connect() as conn:
        rows=pd.read_sql_query("SELECT store_nbr,family,date,onpromotion FROM plans WHERE date=? AND store_nbr=1 AND family IN ('DAIRY','BEVERAGES','BREAD/BAKERY','EGGS','PRODUCE') ORDER BY family",conn,params=[str(next_day)])
    return download(rows,"favorita-plan.csv")


@app.post("/api/predict/batch")
def batch(file:UploadFile=File(...)):
    body=file.file.read(5_000_001)
    if len(body)>5_000_000: raise HTTPException(413,"Use a CSV of 5 MB or less.")
    try: df=pd.read_csv(io.BytesIO(body))
    except (ValueError,UnicodeError) as exc: raise HTTPException(422,"Use a UTF-8 CSV with a header.") from exc
    if df.empty or len(df)>10000 or set(Plan.model_fields)-set(df):
        raise HTTPException(422,"Use the four template columns and 1–10,000 rows.")
    plans=[]
    for i,row in enumerate(df.to_dict("records"),1):
        try: plans.append(Plan.model_validate(row))
        except ValidationError as exc:
            err=exc.errors()[0];raise HTTPException(422,f"Row {i}, {err['loc'][0]}: {err['msg']}") from exc
    return download(df.assign(forecast_units=[round(x,2) for x in forecasts(plans)]),"favorita-forecasts.csv")
