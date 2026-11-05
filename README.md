# SalesSense | Favorita grocery demand

**How many units of dairy will a particular Quito store sell tomorrow?** Select a real city, store and product family, review the number of items on promotion, and generate a one-day-ahead forecast. The same fitted Spark MLlib pipeline scores individual requests and uploaded CSV plans. Sales are measured in units, including fractional quantities for goods sold by weight.

## Start on Windows

Extract the complete ZIP to a short local path such as `C:\Projects\Favorita`. Open PowerShell in the folder containing `app.py`. Use Python 3.10 or 3.11, a 64-bit JDK 21, and native Windows Hadoop tools compatible with your Spark installation. The Spark helper uses `%HADOOP_HOME%\bin` or `C:\hadoop\bin` for `winutils.exe` and `hadoop.dll`. Check `python --version` and `java -version` first.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Open **http://127.0.0.1:8000**. Leave the terminal running. On first use the app creates an indexed SQLite cache from the original CSVs. Allow time for the first overview and for the first Spark forecast. Plotly, the dataset and the fitted model run locally after dependency installation.

### Clone from GitHub

The training CSV is stored with Git LFS because it exceeds GitHub's 100 MB ordinary Git file limit. Install [Git LFS](https://git-lfs.com/), then run `git lfs install` before cloning:

```powershell
git lfs install
git clone https://github.com/anushkazone02/salessense.git
Set-Location salessense
```

Git LFS storage and bandwidth quotas apply. If the large CSV is not downloaded during cloning, run `git lfs pull` from the repository folder.

## Project layout

```text
.
├── api.py                 # FastAPI routes and request validation
├── app.py                 # Local Uvicorn entry point
├── data/                  # Favorita source CSV files
├── model/
│   ├── active.txt         # Selects the active model run
│   └── runs/              # Metrics, analytics, sample predictions and Spark pipeline
├── src/
│   ├── features.py        # Shared Spark feature transformations
│   ├── history.py         # SQLite cache and as-of history features for scoring
│   ├── spark_session.py   # Local Spark configuration
│   └── train_model.py     # Training, validation, evaluation and model publishing
├── web/                   # Dashboard HTML, CSS and JavaScript
├── cache/                 # Generated SQLite index (created at first launch)
└── requirements.txt
```

The `cache/` directory is generated from `data/train.csv`, `data/test.csv` and `data/stores.csv`; it can be rebuilt and is not a source of truth. The active model run is selected by `model/active.txt`. Keep the referenced run directory intact when sharing or deploying the bundled model.

## Bundled run

The validation winner was **Linear regression**. On 81,972 held-out store-family-days, test RMSE was 232.93 units, MAE was 72.38 units, R² was 0.969 and WAPE was 15.0%. On the 81,972 observations with a known prior week, baseline RMSE was 331.07 and the winner's RMSE was 232.93.

## Demonstrate the project

1. **Overview.** Select Quito and DAIRY. Explore monthly unit sales, observations and the number of stores represented. The daily-average chart divides monthly units by the number of store-family-day observations in that month. Export matching rows as CSV.
2. **Sales analytics.** Compare cities, named product families, weekdays and promoted groups. These summaries were computed by Spark on all labeled records. The promotion comparison describes observed sales and does not establish a causal promotion effect.
3. **Model comparison.** Show which of the four regressors had the lowest validation RMSE. Compare the frozen winner against the previous-week benchmark on the same test observations. Inspect predictions and residuals.
4. **Demand forecast.** The form initially selects Quito, Store 1, DAIRY and 16 August 2017. The promotion field is filled from the supplied competition plan. Change the city to see its actual stores. Edit the count to explore a hypothetical promotion plan.
5. **Batch scoring.** Download the template containing five real product-family plans for Store 1, upload it and download the resulting forecasts. The required fields are `store_nbr`, `family`, `date` and `onpromotion`. Output preserves input order and adds `forecast_units`.

## HTTP API

FastAPI's interactive OpenAPI documentation is available at **http://127.0.0.1:8000/docs** while the app is running.

| Method and path | Purpose |
|---|---|
| `GET /api/config` | Return available stores and product families, supported dates and active winner. |
| `GET /api/overview` | Return aggregate counts, units, monthly totals and family summaries. Optional query parameters: `city`, `family`, `start`, `end`. |
| `GET /api/overview.csv` | Download the daily observations matching the same optional filters. |
| `GET /api/analytics` | Return precomputed city, family, weekday and promotion summaries. |
| `GET /api/models` | Return training metrics, model comparison and prediction sample. |
| `GET /api/promotion` | Look up observed/planned promotions and prior-week sales. Requires `store_nbr`, `family` and `day`. |
| `GET /api/template.csv` | Download an example batch-scoring CSV. |
| `POST /api/predict` | Score one JSON plan containing `store_nbr`, `family`, `date` and `onpromotion`. |
| `POST /api/predict/batch` | Upload a CSV with those four columns; returns the input rows with `forecast_units` appended. |

Forecast requests must use a known store and family and a supported date from 1 May through 16 August 2017. Batch uploads are limited to 5 MB and 10,000 rows. Invalid dates, unknown stores/families and invalid field values are rejected with an HTTP 4xx response.

## Observations, features and evaluation

Each row represents one store, one product family and one date. Spark joins `train.csv` with the small `stores.csv` metadata table using a broadcast join. Location and product-family names identify the series in the UI. Model inputs include store format, calendar features, promotion count, change from the prior week's promotion count, and that series' historical sales. Promotion counts refer to how many items in a family are on promotion.

Sales lags use exact calendar offsets of 1, 7, 14, 21 and 28 days. The 7- and 28-day rolling means end the day before the forecast. Missing history is distinguished from zero demand. Same-day sales and same-day transaction counts are excluded. The API reconstructs those history features using indexed lookups and shares the Spark feature transformations with training.

| Period | Use |
|---|---|
| 1 January 2013 – 30 April 2017 | Fit linear regression, decision tree, random forest and gradient-boosted trees on all training observations. |
| 1 May – 30 June 2017 | Select the candidate with the lowest validation RMSE. |
| 1 July – 15 August 2017 | Evaluate the frozen validation winner on previously held-out target dates. |
| 16 August 2017 | First future forecast using the bundled observed history. |

**Horizon.** This is a rolling one-day-ahead evaluation. A prediction for 10 July can use actual sales through 9 July. The competition test file provides future promotion plans and no actual sales. The first day is supported for forecasts. Later competition dates require either newer observed history or a separate multi-step strategy.

**Metrics.** RMSE penalizes large errors, while MAE is the average absolute miss in units. R² measures the fraction of variation explained. WAPE is total absolute error divided by total actual unit sales. These are pooled scores across all store-family-days. High-volume families strongly influence RMSE. Compare models and baselines on identical targets and dates.

**Baseline.** For each test date, use the same store and product family's actual sales exactly seven days earlier. For the comparison table, only use rows with an observed prior week. Negative model estimates are clipped to zero in evaluation and serving.

## Included data and reproducibility

All seven CSVs come from the supplied [Kaggle Favorita Store Sales competition archive](https://www.kaggle.com/competitions/favorita-grocery-sales-forecasting/data). Training uses labeled sales and store metadata. Future plans are read from `test.csv`. The oil, holiday, transaction and sample submission files are retained as source material. The run's metrics, Spark aggregates, prediction sample and fitted pipeline are under the directory named by `model/active.txt`.

To retrain, stop the web server, run `.\.venv\Scripts\python.exe -m src.train_model` and restart with `.\.venv\Scripts\python.exe app.py`. The new complete run is published after its artifacts are written. Spark defaults to two local worker threads. Remove the rebuildable `cache` folder only if you manually replace the source data.

## Troubleshooting

- **Java or Spark startup error:** confirm that `java -version` works and that the installed JDK is 64-bit. This project targets JDK 21 and PySpark 4.2.0.
- **Windows native Hadoop error:** install compatible `winutils.exe` and `hadoop.dll`, then set `HADOOP_HOME` to their parent directory (or place them under `C:\hadoop\bin`).
- **Missing model files:** check that `model/active.txt` names an existing directory under `model/runs/` and that the directory contains the `pipeline/` artifact.
- **First dashboard load is slow:** the application builds indexed SQLite tables from the source CSVs on first use; subsequent launches reuse `cache/favorita.sqlite`.
- **Forecast fails while app starts:** the first Spark model load can take time. Keep the server process running and inspect its terminal output for the underlying Spark error.
