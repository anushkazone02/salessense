# SalesSense — Viva Preparation (Q&A)

## Apache Spark

**1. What is Apache Spark, and why did you use it for this project?**
Apache Spark is an open-source distributed data processing engine. It processes data in
parallel across multiple CPU cores (or machines, in a cluster) using an in-memory computation
model, which makes it much faster than disk-based systems like Hadoop MapReduce for iterative
workloads like machine learning. I used it here so that every stage — loading, cleaning,
feature engineering, model training, and prediction — is built on an architecture that scales
to datasets far larger than this project's 9,994 rows, without rewriting the code.

**2. What does `local[*]` mean in your SparkSession configuration?**
It tells Spark to run in local mode using all available CPU cores on the current machine as
"workers," rather than connecting to a remote cluster. It's how you develop and test Spark
code on a single machine. To run on an actual cluster, only the master URL would change
(e.g. to a YARN or Spark-standalone cluster address) — the rest of the code stays identical.

**3. What is a Spark DataFrame, and how is it different from a pandas DataFrame?**
A Spark DataFrame is a distributed collection of data organized into named columns, similar in
concept to a pandas DataFrame, but its operations are lazily evaluated and executed in parallel
across partitions of the data, potentially across many machines. A pandas DataFrame lives
entirely in one process's memory on one machine.

**4. What is lazy evaluation in Spark, and why does it matter?**
Spark builds a logical plan of transformations (like `filter`, `groupBy`) without executing
them immediately. Execution only happens when an "action" (like `count()`, `show()`, `collect()`)
is called. This lets Spark's optimizer combine and reorder operations for efficiency before
running anything.

**5. What is a Spark ML Pipeline, and why use one instead of calling transformers manually?**
A Pipeline chains multiple data transformation and modeling stages (e.g. StringIndexer →
OneHotEncoder → VectorAssembler → StandardScaler → LinearRegression) into a single object that
can be fit and applied as one unit. This guarantees the exact same sequence of transformations
is applied consistently at training and at inference time, and lets the whole pipeline be saved
and reloaded as a single artifact.

**6. What do StringIndexer and OneHotEncoder do, and why are both needed?**
StringIndexer converts a categorical string column (e.g. "Furniture", "Technology") into a
numeric index column. OneHotEncoder then converts that numeric index into a sparse binary
vector, so the model doesn't wrongly interpret the indices as having an ordinal relationship
(e.g. that "Technology" > "Furniture" numerically).

**7. What does VectorAssembler do?**
It combines multiple individual feature columns (numeric columns and one-hot encoded vectors)
into a single feature vector column, which is the input format Spark MLlib's regression and
classification algorithms require.

**8. Why did you use StandardScaler?**
StandardScaler standardizes the feature vector to zero mean and unit variance. This helps
Linear Regression's optimizer converge more reliably and keeps the learned coefficients on a
comparable scale, since raw features here have very different ranges (e.g. Quantity 1–14 vs.
one-hot 0/1 columns).

**9. What does `handleInvalid="keep"` do in your StringIndexer, and why did you set it?**
It tells the indexer to map any category not seen during training (e.g. a new Sub-Category in
future data) to an extra "unknown" index bucket instead of throwing an error. This makes the
pipeline robust to slightly different data at inference time — important for the batch
prediction feature.

## Linear Regression

**10. Why did you choose Linear Regression instead of a more complex model?**
The project brief specifically asked for Spark MLlib Linear Regression as the core learning
algorithm, and it's a good baseline: it's fast to train, easy to interpret (coefficients show
each feature's direction and rough magnitude of effect), and it's the reference point against
which more complex models would later be compared.

**11. What do the model's coefficients represent?**
Each coefficient is the change in predicted Sales associated with a one-standard-deviation
increase in that (scaled) feature, holding other features constant — because the features were
standardized before training.

**12. What is regularization, and why did you set `regParam=0.1`?**
Regularization adds a penalty term to the loss function to discourage overly large coefficients,
which helps prevent overfitting and improves numerical stability, especially with one-hot
encoded features that can be collinear. `regParam=0.1` applies a modest L2 (ridge-style)
penalty, since `elasticNetParam=0.0`.

**13. How did you split your data into training and test sets?**
An 80/20 random split using `randomSplit([0.8, 0.2], seed=42)`, giving 8,042 training rows and
1,952 test rows. The fixed seed makes the split reproducible.

**14. Why is it important that the Pipeline is fit only on the training set?**
If steps like StandardScaler or StringIndexer were fit on the full dataset (including test
data), statistics from the test set (like its mean/variance) would leak into the training
process, giving an overly optimistic evaluation that wouldn't reflect real-world performance on
genuinely unseen data.

## RMSE / MAE / R²

**15. What is RMSE, and what does your RMSE of 536.33 mean?**
Root Mean Squared Error is the square root of the average squared difference between predicted
and actual Sales. It's in the same unit as Sales (₹), and because errors are squared before
averaging, it penalizes large errors more than small ones. An RMSE of 536.33 means the model's
typical prediction error is on the order of ₹536.

**16. What is MAE, and how is it different from RMSE?**
Mean Absolute Error is the average of the absolute differences between predicted and actual
values, without squaring. It's more robust to outliers than RMSE and easier to interpret
directly ("predictions are off by about ₹228 on average"). RMSE ≥ MAE always; the gap between
them (536 vs 228 here) indicates the presence of some large errors pulling RMSE up — consistent
with the dataset's few very high-value orders.

**17. What does an R² of 0.292 mean, and is it a good result?**
R² measures the proportion of variance in Sales explained by the model, from 0 to 1. An R² of
0.292 means the model explains about 29% of the variance in Sales. It's a modest but honest
result: Sales is highly right-skewed (a handful of very large orders), and Linear Regression
can't capture non-linear interactions between features, so a perfect or very high R² was never
realistic for this model/data combination. It's more meaningful in context — train R² (0.238)
being *lower* than test R² shows the model isn't overfitting.

**18. Why is Profit not used as a feature, even though it correlates with Sales?**
In this dataset, Profit is arithmetically derived from Sales (and cost), so it has an
artificially strong correlation (0.479) with the target that isn't a genuine independent signal
— it's closer to a restatement of the answer. Including it would cause target leakage and give
a misleadingly high evaluation score that wouldn't generalize to real prediction scenarios
where Profit isn't known in advance.

## GUI (Streamlit)

**19. Why did you choose Streamlit for the GUI instead of Flask/Django?**
Streamlit lets you build an interactive, stateful data application in pure Python, without
writing separate HTML/CSS/JavaScript front-end code, which is well suited for quickly building
a polished analytics and ML-prediction interface. Flask/Django would require significantly more
boilerplate for the same result in the scope of a mini-project.

**20. How does the Streamlit app avoid reinitializing Spark on every user interaction?**
Using Streamlit's caching decorators: `@st.cache_resource` caches the SparkSession and the
loaded model object across reruns (so they're created once per session), and `@st.cache_data`
caches the cleaned dataset and precomputed aggregations, so expensive Spark computations aren't
repeated every time a widget is touched.

**21. How does batch prediction work end-to-end?**
The user uploads a CSV; it's read into pandas, validated against the required columns, then
converted into a Spark DataFrame matching the model's expected schema, passed through
`model.transform()` (running the exact same fitted Pipeline used at training time), and the
resulting predictions are joined back onto the original rows and offered as a downloadable CSV.

## Limitations & Future Scope

**22. What are the main limitations of this system?**
The model's predictive accuracy is modest (R² ≈ 0.29) because Linear Regression is purely
linear and the target is heavily skewed; no hyperparameter tuning beyond one fixed
regularization value was performed; and while the architecture is designed to scale to a
cluster, this demonstration runs Spark in local mode on a single machine.

**23. How would you improve this system given more time?**
Try Spark MLlib's tree-based regressors (RandomForestRegressor, GBTRegressor) to capture
non-linear relationships; use CrossValidator with a parameter grid for proper hyperparameter
tuning; log-transform the Sales target to reduce the influence of extreme high-value orders;
and test the pipeline against an actual multi-node Spark cluster with a much larger dataset.
