"""Indexed CSV cache and strict as-of queries used by the local dashboard."""
from pathlib import Path
from contextlib import contextmanager
from functools import lru_cache
from uuid import uuid4
import sqlite3
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]


@lru_cache(maxsize=1)
def database():
    folder=ROOT/"cache";folder.mkdir(exist_ok=True)
    target=folder/"favorita.sqlite"
    if target.exists(): return target
    tmp=folder/(uuid4().hex+".sqlite");conn=sqlite3.connect(tmp)
    try:
        pd.read_csv(ROOT/"data/stores.csv").to_sql("stores",conn,index=False)
        for csv,table in [("train","daily"),("test","plans")]:
            for chunk in pd.read_csv(ROOT/f"data/{csv}.csv",chunksize=60000):
                chunk.to_sql(table,conn,if_exists="append",index=False)
            conn.execute(f"CREATE UNIQUE INDEX {table}_series_date ON {table}(store_nbr,family,date)")
        conn.execute("CREATE UNIQUE INDEX store_id ON stores(store_nbr)")
        conn.commit()
    finally:
        conn.close()
    tmp.replace(target)
    return target


@contextmanager
def connect():
    conn=sqlite3.connect(database());conn.row_factory=sqlite3.Row
    try: yield conn
    finally: conn.close()


def history_features(records):
    from src.features import LAGS
    rows=[(i,p["store_nbr"],p["family"],str(p["date"]),p["onpromotion"]) for i,p in enumerate(records)]
    lag_cols=[f"MAX(CASE WHEN h.date=date(i.date,'-{n} days') THEN h.sales END) AS lag{n}" for n in LAGS]
    sql=f"""SELECT i.*,s.type,AVG(h.sales) AS mean28,
        AVG(CASE WHEN h.date>=date(i.date,'-7 days') THEN h.sales END) AS mean7,
        MAX(CASE WHEN h.date=date(i.date,'-7 days') THEN h.onpromotion END) AS prior_promo,
        {','.join(lag_cols)} FROM incoming i JOIN stores s ON s.store_nbr=i.store_nbr
        LEFT JOIN daily h ON h.store_nbr=i.store_nbr AND h.family=i.family
        AND h.date BETWEEN date(i.date,'-28 days') AND date(i.date,'-1 day')
        GROUP BY i.line ORDER BY i.line"""
    with connect() as conn:
        conn.execute("CREATE TEMP TABLE incoming(line INT,store_nbr INT,family TEXT,date TEXT,onpromotion INT)")
        conn.executemany("INSERT INTO incoming VALUES(?,?,?,?,?)",rows)
        return pd.read_sql_query(sql,conn)
