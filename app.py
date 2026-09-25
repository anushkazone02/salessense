"""
app.py
--------
SalesSense - Scalable Sales Prediction & Analytics System
Main Streamlit application entry point.

Run with:  streamlit run app.py    (from the project root)

The app loads the Spark-trained PipelineModel (src/train_model.py must
have been run at least once) and provides:
  1. Dashboard        - KPIs, trends, filters
  2. Sales Prediction  - single-record prediction form
  3. Batch Prediction  - CSV upload -> bulk predictions -> download
  4. Model Performance - RMSE/MAE/R2, actual vs predicted, residuals
  5. Analytics         - deeper interactive charts
  6. About             - project/tech overview
"""

import json
import os
import sys

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config import (
    METRICS_PATH, PREDICTIONS_SAMPLE_PATH, TRAINED_MODEL_PATH,
)
from src.spark_session import get_spark_session
from src.preprocessing import get_clean_dataframe
from src.feature_engineering import add_date_features
from src.prediction import load_model, predict_single, predict_batch
from src import analytics as an

# ---------------------------------------------------------------------------
# Page config & global style
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="SalesSense",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stApp {
        background: #f3f3f1;
    }
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2.5rem;
        max-width: 1500px;
    }
    [data-testid="stSidebar"] {
        background: #0f3d2f;
        border-right: 1px solid rgba(255,255,255,0.08);
    }
    [data-testid="stSidebarNav"] {
        padding-top: 0.35rem;
    }
    .sidebar-brand {
        color: #f4f7f5;
        font-size: 2rem;
        font-weight: 700;
        line-height: 1.1;
        padding: 1.1rem 1rem 0.45rem 1rem;
        letter-spacing: -0.06em;
    }
    .sidebar-section {
        color: rgba(255,255,255,0.58);
        font-size: 0.72rem;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        padding: 1rem 1rem 0.5rem 1rem;
    }
    [data-testid="stSidebar"] .stRadio {
        padding: 0 0.5rem;
    }
    [data-testid="stSidebar"] label {
        color: rgba(255,255,255,0.9);
        font-size: 1.02rem;
        font-weight: 500;
        padding: 0.7rem 0.8rem;
        border-radius: 10px;
    }
    [data-testid="stSidebar"] label:hover {
        background: rgba(255,255,255,0.04);
    }
    [data-testid="stSidebar"] .stRadio > div {
        gap: 0.2rem;
    }
    [data-testid="stSidebar"] .stRadio input[type="radio"] {
        accent-color: #8fcf64;
    }
    h1 {
        font-size: 2.2rem !important;
        font-weight: 700 !important;
        color: #1a1a1a !important;
        letter-spacing: -0.04em !important;
        margin-bottom: 0.15rem !important;
    }
    .stMarkdown p, .stMarkdown li, .stMarkdown span {
        color: #3f453f;
        font-size: 0.96rem;
    }
    .stMarkdown strong {
        color: #1a1a1a;
    }
    .kpi-card {
        background: #f7f7f4;
        border: 1px solid rgba(17, 24, 39, 0.08);
        border-radius: 18px;
        padding: 1.1rem 1.2rem;
        min-height: 145px;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.02);
    }
    .kpi-label {
        color: #646a66;
        font-size: 0.8rem;
        text-transform: none;
        letter-spacing: 0;
        margin-bottom: 0.5rem;
    }
    .kpi-value {
        color: #171717;
        font-size: 1.85rem;
        font-weight: 700;
        letter-spacing: -0.05em;
        line-height: 1.2;
    }
    .kpi-sub {
        color: #6d726e;
        font-size: 0.8rem;
        margin-top: 0.45rem;
    }
    .metric-card {
        background: #ffffff;
        border: 1px solid rgba(17, 24, 39, 0.08);
        border-radius: 16px;
        padding: 1rem 1.1rem;
        min-height: 130px;
        box-shadow: 0 3px 10px rgba(15, 23, 42, 0.03);
    }
    .metric-label {
        color: #646a66;
        font-size: 0.8rem;
        margin-bottom: 0.55rem;
    }
    .metric-value {
        color: #171717;
        font-size: 1.7rem;
        font-weight: 700;
        letter-spacing: -0.05em;
        line-height: 1.2;
    }
    .metric-sub {
        color: #6d726e;
        font-size: 0.8rem;
        margin-top: 0.4rem;
    }
    .section-title {
        color: #1d1d1d;
        font-size: 1.15rem;
        font-weight: 700;
        margin: 1rem 0 0.75rem 0;
        letter-spacing: -0.02em;
    }
    .secondary-panel {
        background: #f7f7f4;
        border: 1px solid rgba(17, 24, 39, 0.08);
        border-radius: 16px;
        padding: 0.9rem 1rem;
    }
    .muted-note {
        color: #66706a;
        font-size: 0.82rem;
    }
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
    }
    .stDataFrame table {
        border-collapse: separate;
        border-spacing: 0;
    }
    .prediction-card {
        background: linear-gradient(135deg, #0f3d2f 0%, #1c5f47 100%);
        border-radius: 18px;
        padding: 34px;
        text-align: center;
        margin-top: 18px;
        box-shadow: 0 10px 30px rgba(15, 61, 47, 0.25);
    }
    .prediction-label {
        color: #cfe9dc;
        font-size: 1rem;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    .prediction-value {
        color: white;
        font-size: 3rem;
        font-weight: 800;
    }
    .metric-explainer {
        background: #f7f7f4;
        border-radius: 10px;
        padding: 14px 18px;
        border: 1px solid rgba(17, 24, 39, 0.08);
        font-size: 0.9rem;
        color: #4b514c;
        margin-bottom: 10px;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Cached resources: Spark session, cleaned data, trained model, metrics
# ---------------------------------------------------------------------------
@st.cache_resource(show_spinner="Starting Spark session...")
def init_spark():
    return get_spark_session(app_name="SalesSense-Streamlit")


@st.cache_data(show_spinner="Loading and cleaning data with Spark...")
def load_clean_pandas():
    spark = init_spark()
    df = get_clean_dataframe(spark)
    df = add_date_features(df)
    df = df.cache()
    pdf = an.get_raw_pandas_for_filters(df)
    kpis = an.get_summary_kpis(df)
    by_month = an.sales_by_month(df)
    by_weekday = an.sales_by_weekday(df)
    by_category = an.sales_by_category(df)
    by_subcategory = an.sales_by_subcategory(df)
    by_region = an.sales_by_region(df)
    by_segment = an.sales_by_segment(df)
    top_n = an.top_products(df, n=10)
    disc_scatter = an.discount_vs_sales_sample(df)
    return {
        "raw": pdf, "kpis": kpis, "by_month": by_month, "by_weekday": by_weekday,
        "by_category": by_category, "by_subcategory": by_subcategory,
        "by_region": by_region, "by_segment": by_segment,
        "top_products": top_n, "disc_scatter": disc_scatter,
    }


@st.cache_resource(show_spinner="Loading trained Spark ML model...")
def load_trained_model():
    spark = init_spark()
    if not os.path.exists(TRAINED_MODEL_PATH):
        return None
    return load_model(spark)


@st.cache_data
def load_metrics():
    if not os.path.exists(METRICS_PATH):
        return None
    with open(METRICS_PATH) as f:
        return json.load(f)


@st.cache_data
def load_prediction_sample():
    if not os.path.exists(PREDICTIONS_SAMPLE_PATH):
        return None
    return pd.read_csv(PREDICTIONS_SAMPLE_PATH)


# ---------------------------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------------------------
st.sidebar.markdown('<div class="sidebar-brand">SalesSense</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="sidebar-section">Menu</div>', unsafe_allow_html=True)

PAGES = [
    "Dashboard",
    "Sales Prediction",
    "Batch Prediction",
    "Model Performance",
    "Analytics",
    "About Project",
]
page = st.sidebar.radio("Navigate", PAGES, label_visibility="collapsed")

st.sidebar.markdown("---")
st.sidebar.caption("Sales operations overview")

CATEGORY_SUBCATEGORY = {
    "Furniture": ["Bookcases", "Chairs", "Furnishings", "Tables"],
    "Office Supplies": ["Appliances", "Art", "Binders", "Envelopes", "Fasteners",
                         "Labels", "Paper", "Storage", "Supplies"],
    "Technology": ["Accessories", "Copiers", "Machines", "Phones"],
}
REGIONS = ["West", "East", "Central", "South"]
SEGMENTS = ["Consumer", "Corporate", "Home Office"]
SHIP_MODES = ["Standard Class", "Second Class", "First Class", "Same Day"]
MONTH_NAMES = ["January", "February", "March", "April", "May", "June", "July",
               "August", "September", "October", "November", "December"]
WEEKDAY_NAMES = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

CHART_LAYOUT_DEFAULTS = dict(
    template="simple_white",
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#1f2937"),
)


def _axis_style():
    return dict(title_font=dict(color="#1f2937"), tickfont=dict(color="#1f2937"))


# ---------------------------------------------------------------------------
# PAGE: Dashboard
# ---------------------------------------------------------------------------
def render_dashboard():
    st.title("Sales Dashboard")
    st.caption("Real-time view over the Superstore sales dataset, processed with Apache Spark")

    data = load_clean_pandas()
    raw = data["raw"]

    with st.expander("Filters", expanded=False):
        c1, c2, c3 = st.columns(3)
        min_date, max_date = raw["Order_Date_Parsed"].min(), raw["Order_Date_Parsed"].max()
        date_range = c1.date_input("Order date range", value=(min_date, max_date),
                                    min_value=min_date, max_value=max_date)
        cat_filter = c2.multiselect("Category", sorted(raw["Category"].unique()))
        region_filter = c3.multiselect("Region", sorted(raw["Region"].unique()))

    filtered = raw.copy()
    filtered["Order_Date_Parsed"] = pd.to_datetime(filtered["Order_Date_Parsed"])
    if isinstance(date_range, tuple) and len(date_range) == 2:
        filtered = filtered[
            (filtered["Order_Date_Parsed"] >= pd.Timestamp(date_range[0])) &
            (filtered["Order_Date_Parsed"] <= pd.Timestamp(date_range[1]))
        ]
    if cat_filter:
        filtered = filtered[filtered["Category"].isin(cat_filter)]
    if region_filter:
        filtered = filtered[filtered["Region"].isin(region_filter)]

    total_sales = filtered["Sales"].sum()
    avg_sales = filtered["Sales"].mean() if len(filtered) else 0
    num_txn = len(filtered)
    best_cat = filtered.groupby("Category")["Sales"].sum().idxmax() if len(filtered) else "-"

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-label">Total Sales</div>
            <div class="kpi-value">₹{total_sales:,.0f}</div>
            <div class="kpi-sub">across {num_txn:,} transactions</div></div>""", unsafe_allow_html=True)
    with k2:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-label">Average Sale</div>
            <div class="kpi-value">₹{avg_sales:,.2f}</div>
            <div class="kpi-sub">per transaction</div></div>""", unsafe_allow_html=True)
    with k3:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-label">Transactions</div>
            <div class="kpi-value">{num_txn:,}</div>
            <div class="kpi-sub">order line items</div></div>""", unsafe_allow_html=True)
    with k4:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-label">Top Category</div>
            <div class="kpi-value">{best_cat}</div>
            <div class="kpi-sub">by total sales</div></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown('<div class="section-title">Sales Trend Over Time</div>', unsafe_allow_html=True)
    if len(filtered):
        monthly = (
            filtered.assign(YearMonth=filtered["Order_Date_Parsed"].dt.to_period("M").astype(str))
            .groupby("YearMonth", as_index=False)["Sales"].sum()
            .sort_values("YearMonth")
        )
        fig = px.line(monthly, x="YearMonth", y="Sales", markers=True,
                       color_discrete_sequence=["#1c5f47"])
        fig.update_layout(**CHART_LAYOUT_DEFAULTS, height=380,
                           xaxis_title="Month", yaxis_title="Total Sales (₹)",
                           legend_title_text="Sales",
                           xaxis=_axis_style(), yaxis=_axis_style())
        st.plotly_chart(fig, width='stretch')
    else:
        st.info("No data for the selected filters.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-title">Sales by Category</div>', unsafe_allow_html=True)
        if len(filtered):
            cat_agg = filtered.groupby("Category", as_index=False)["Sales"].sum()
            fig = px.pie(cat_agg, names="Category", values="Sales", hole=0.5,
                         color_discrete_sequence=px.colors.sequential.Greens_r)
            fig.update_layout(**CHART_LAYOUT_DEFAULTS, height=340,
                               legend_title_text="Category",
                               margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig, width='stretch')
    with col2:
        st.markdown('<div class="section-title">Sales by Region</div>', unsafe_allow_html=True)
        if len(filtered):
            reg_agg = filtered.groupby("Region", as_index=False)["Sales"].sum().sort_values("Sales")
            fig = px.bar(reg_agg, x="Sales", y="Region", orientation="h",
                         color_discrete_sequence=["#1c5f47"])
            fig.update_layout(**CHART_LAYOUT_DEFAULTS, height=340,
                               xaxis_title="Sales (₹)", yaxis_title="Region",
                               xaxis=_axis_style(), yaxis=_axis_style())
            st.plotly_chart(fig, width='stretch')


# ---------------------------------------------------------------------------
# PAGE: Sales Prediction
# ---------------------------------------------------------------------------
def render_prediction():
    st.title("Sales Prediction")
    st.caption("Enter order details to get a predicted sales value from the trained Spark MLlib model")

    model = load_trained_model()
    if model is None:
        st.error("No trained model found. Please run `python -m src.train_model` first.")
        return

    with st.form("prediction_form"):
        c1, c2, c3 = st.columns(3)
        category = c1.selectbox("Category", list(CATEGORY_SUBCATEGORY.keys()))
        subcategory = c2.selectbox("Sub-Category", CATEGORY_SUBCATEGORY[category])
        segment = c3.selectbox("Customer Segment", SEGMENTS)

        c4, c5, c6 = st.columns(3)
        region = c4.selectbox("Region", REGIONS)
        ship_mode = c5.selectbox("Ship Mode", SHIP_MODES)
        quantity = c6.number_input("Quantity", min_value=1, max_value=20, value=2)

        c7, c8, c9 = st.columns(3)
        discount = c7.slider("Discount", min_value=0.0, max_value=0.8, value=0.0, step=0.05)
        month = c8.selectbox("Order Month", MONTH_NAMES, index=5)
        weekday = c9.selectbox("Order Day of Week", WEEKDAY_NAMES, index=0)

        submitted = st.form_submit_button("Predict Sales", width='stretch')

    if submitted:
        spark = init_spark()
        record = {
            "Category": category,
            "Sub_Category": subcategory,
            "Segment": segment,
            "Region": region,
            "Ship_Mode": ship_mode,
            "Quantity": quantity,
            "Discount": discount,
            "Order_Month": MONTH_NAMES.index(month) + 1,
            "Order_DayOfWeek": WEEKDAY_NAMES.index(weekday) + 1,
        }
        with st.spinner("Running prediction through the Spark ML pipeline..."):
            predicted_sales = predict_single(spark, model, record)

        st.markdown(f"""
        <div class="prediction-card">
            <div class="prediction-label">Predicted Sales</div>
            <div class="prediction-value">₹{predicted_sales:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("View input sent to the model"):
            st.json(record)


# ---------------------------------------------------------------------------
# PAGE: Batch Prediction
# ---------------------------------------------------------------------------
def render_batch_prediction():
    st.title("Batch Prediction")
    st.caption("Upload a CSV of new records to generate sales predictions in bulk")

    required_cols = ["Category", "Sub_Category", "Segment", "Region", "Ship_Mode",
                      "Quantity", "Discount", "Order_Month", "Order_DayOfWeek"]
    st.markdown(f"**Required columns:** `{', '.join(required_cols)}`")

    template_df = pd.DataFrame([{
        "Category": "Furniture", "Sub_Category": "Chairs", "Segment": "Consumer",
        "Region": "West", "Ship_Mode": "Standard Class", "Quantity": 3,
        "Discount": 0.1, "Order_Month": 6, "Order_DayOfWeek": 3,
    }])
    st.download_button("Download CSV template", template_df.to_csv(index=False),
                        file_name="salessense_batch_template.csv", mime="text/csv")

    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

    if uploaded_file is not None:
        try:
            input_df = pd.read_csv(uploaded_file)
        except Exception as e:
            st.error(f"Could not read the uploaded file as CSV: {e}")
            return

        st.write("Preview of uploaded data:")
        st.dataframe(input_df.head(10), width='stretch')

        model = load_trained_model()
        if model is None:
            st.error("No trained model found. Please run `python -m src.train_model` first.")
            return

        if st.button("Run Batch Prediction", width='stretch'):
            spark = init_spark()
            try:
                with st.spinner(f"Processing {len(input_df)} records through Spark..."):
                    result_df = predict_batch(spark, model, input_df)
                st.success(f"Generated predictions for {len(result_df)} records.")
                st.dataframe(result_df, width='stretch')
                st.download_button(
                    "Download Predictions CSV",
                    result_df.to_csv(index=False),
                    file_name="salessense_predictions.csv",
                    mime="text/csv",
                    width='stretch',
                )
                fig = px.histogram(result_df, x="Predicted_Sales", nbins=30,
                                    color_discrete_sequence=["#1c5f47"])
                fig.update_layout(**CHART_LAYOUT_DEFAULTS, height=320,
                                   title="Distribution of Predicted Sales",
                                   xaxis=_axis_style(), yaxis=_axis_style())
                st.plotly_chart(fig, width='stretch')
            except ValueError as e:
                st.error(str(e))
            except Exception as e:
                st.error(f"Prediction failed: {e}")


# ---------------------------------------------------------------------------
# PAGE: Model Performance
# ---------------------------------------------------------------------------
def render_model_performance():
    st.title("Model Performance")
    st.caption("Evaluation of the Spark MLlib Linear Regression model on the held-out test set")

    metrics = load_metrics()
    sample = load_prediction_sample()

    if metrics is None:
        st.error("No metrics found. Please run `python -m src.train_model` first.")
        return

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">RMSE</div>
            <div class="metric-value">{metrics['rmse']:.2f}</div>
            <div class="metric-sub">Root Mean Squared Error</div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">MAE</div>
            <div class="metric-value">{metrics['mae']:.2f}</div>
            <div class="metric-sub">Mean Absolute Error</div></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">R² Score</div>
            <div class="metric-value">{metrics['r2']:.3f}</div>
            <div class="metric-sub">Coefficient of Determination</div></div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Training Time</div>
            <div class="metric-value">{metrics['training_time_seconds']:.2f}s</div>
            <div class="metric-sub">Model training duration</div></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">What do these metrics mean?</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="metric-explainer"><b>RMSE (Root Mean Squared Error)</b> — the typical size of the model's
    prediction error, in the same units as Sales (₹). Larger errors are penalized more heavily,
    so RMSE is sensitive to big misses.</div>
    <div class="metric-explainer"><b>MAE (Mean Absolute Error)</b> — the average absolute difference
    between predicted and actual sales, without over-weighting large errors. Easier to interpret
    directly: "on average, predictions are off by ₹X."</div>
    <div class="metric-explainer"><b>R² (R-squared)</b> — the proportion of variance in Sales that the
    model explains, from 0 (no better than predicting the average) to 1 (perfect fit).</div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">Training Details</div>', unsafe_allow_html=True)
    d1, d2, d3, d4 = st.columns(4)
    d1.metric("Training rows", f"{metrics['train_rows']:,}")
    d2.metric("Test rows", f"{metrics['test_rows']:,}")
    d3.metric("Training time", f"{metrics['training_time_seconds']}s")
    d4.metric("Feature vector size", metrics['feature_vector_size'])

    st.markdown(f"""
    <div class="metric-explainer">
    Train RMSE: <b>{metrics['train_rmse']:.2f}</b> · Train R²: <b>{metrics['train_r2']:.3f}</b> —
    test performance is close to (not worse than) training performance, indicating the model
    is not overfitting the training data.
    </div>
    """, unsafe_allow_html=True)

    if sample is not None:
        st.markdown('<div class="section-title">Actual vs Predicted Sales (test sample)</div>', unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=sample["actual_sales"], y=sample["predicted_sales"], mode="markers",
            marker=dict(color="#1c5f47", size=6, opacity=0.6), name="Predictions"
        ))
        max_val = max(sample["actual_sales"].max(), sample["predicted_sales"].max())
        fig.add_trace(go.Scatter(x=[0, max_val], y=[0, max_val], mode="lines",
                                  line=dict(color="#8fcf64", dash="dash"), name="Perfect prediction"))
        fig.update_layout(**CHART_LAYOUT_DEFAULTS, height=420,
                           xaxis_title="Actual Sales (₹)", yaxis_title="Predicted Sales (₹)",
                           xaxis=_axis_style(), yaxis=_axis_style())
        st.plotly_chart(fig, width='stretch')

        st.markdown('<div class="section-title">Residual Distribution</div>', unsafe_allow_html=True)
        fig2 = px.histogram(sample, x="residual", nbins=40, color_discrete_sequence=["#1c5f47"])
        fig2.update_layout(**CHART_LAYOUT_DEFAULTS, height=340,
                            xaxis_title="Residual (Actual − Predicted)",
                            xaxis=_axis_style(), yaxis=_axis_style())
        st.plotly_chart(fig2, width='stretch')


# ---------------------------------------------------------------------------
# PAGE: Analytics
# ---------------------------------------------------------------------------
def render_analytics():
    st.title("Sales Analytics")
    st.caption("Deeper interactive breakdowns of the dataset, aggregated with Spark")

    data = load_clean_pandas()

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-title">Top 10 Products by Sales</div>', unsafe_allow_html=True)
        top_df = data["top_products"].sort_values("Total_Sales")
        fig = px.bar(top_df, x="Total_Sales", y="Product_Name", orientation="h",
                     color_discrete_sequence=["#1c5f47"])
        fig.update_layout(**CHART_LAYOUT_DEFAULTS, height=420,
                           xaxis_title="Total Sales (₹)", yaxis_title="Product Name",
                           xaxis=_axis_style(),
                           yaxis=dict(title_font=dict(color="#1f2937"), tickfont=dict(color="#1f2937", size=9)))
        st.plotly_chart(fig, width='stretch')

    with col2:
        st.markdown('<div class="section-title">Sales by Sub-Category</div>', unsafe_allow_html=True)
        sub_df = data["by_subcategory"].sort_values("Total_Sales")
        fig = px.bar(sub_df, x="Total_Sales", y="Sub_Category", orientation="h",
                     color_discrete_sequence=["#8fcf64"])
        fig.update_layout(**CHART_LAYOUT_DEFAULTS, height=420,
                           xaxis_title="Total Sales (₹)", yaxis_title="Sub-Category",
                           xaxis=_axis_style(), yaxis=_axis_style())
        st.plotly_chart(fig, width='stretch')

    col3, col4 = st.columns(2)
    with col3:
        st.markdown('<div class="section-title">Quantity vs Sales</div>', unsafe_allow_html=True)
        fig = px.scatter(data["disc_scatter"], x="Quantity", y="Sales", color="Category",
                          opacity=0.6, color_discrete_sequence=px.colors.qualitative.Prism)
        fig.update_layout(**CHART_LAYOUT_DEFAULTS, height=380,
                           xaxis_title="Quantity", yaxis_title="Sales (₹)",
                           xaxis=_axis_style(), yaxis=_axis_style())
        st.plotly_chart(fig, width='stretch')

    with col4:
        st.markdown('<div class="section-title">Discount vs Sales</div>', unsafe_allow_html=True)
        fig = px.scatter(data["disc_scatter"], x="Discount", y="Sales", color="Category",
                          opacity=0.6, color_discrete_sequence=px.colors.qualitative.Prism)
        fig.update_layout(**CHART_LAYOUT_DEFAULTS, height=380,
                           xaxis_title="Discount", yaxis_title="Sales (₹)",
                           xaxis=_axis_style(), yaxis=_axis_style())
        st.plotly_chart(fig, width='stretch')

    st.markdown('<div class="section-title">Sales by Day of Week</div>', unsafe_allow_html=True)
    weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    wd = data["by_weekday"].copy()
    wd["Weekday"] = pd.Categorical(wd["Weekday"], categories=weekday_order, ordered=True)
    wd = wd.sort_values("Weekday")
    fig = px.bar(wd, x="Weekday", y="Total_Sales", color_discrete_sequence=["#1c5f47"])
    fig.update_layout(**CHART_LAYOUT_DEFAULTS, height=340,
                       xaxis_title="Day of Week", yaxis_title="Total Sales (₹)",
                       xaxis=_axis_style(), yaxis=_axis_style())
    st.plotly_chart(fig, width='stretch')

    st.markdown('<div class="section-title">Sales by Customer Segment</div>', unsafe_allow_html=True)
    fig = px.bar(data["by_segment"].sort_values("Total_Sales"), x="Total_Sales", y="Segment",
                 orientation="h", color_discrete_sequence=["#8fcf64"])
    fig.update_layout(**CHART_LAYOUT_DEFAULTS, height=280,
                       xaxis_title="Total Sales (₹)", yaxis_title="Customer Segment",
                       xaxis=_axis_style(), yaxis=_axis_style())
    st.plotly_chart(fig, width='stretch')


# ---------------------------------------------------------------------------
# PAGE: About
# ---------------------------------------------------------------------------
def render_about():
    st.title("About SalesSense")
    st.markdown("""
    **SalesSense** is a scalable sales prediction and analytics system built as a college
    mini-project to demonstrate distributed data processing with **Apache Spark** and
    machine learning with **Spark MLlib**, wrapped in an interactive **Streamlit** GUI.
    """)

    st.markdown('<div class="section-title">Problem Statement</div>', unsafe_allow_html=True)
    st.write(
        "Develop a scalable sales prediction system using historical sales data: preprocess "
        "and process the dataset using Apache Spark, engineer features, train a Linear "
        "Regression model with Spark MLlib, predict sales, evaluate performance, and surface "
        "useful analytics through an interactive GUI."
    )

    st.markdown('<div class="section-title">Tech Stack</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.markdown("**Data Processing**\n- Apache Spark (PySpark)\n- Spark SQL DataFrame API")
    c2.markdown("**Machine Learning**\n- Spark MLlib\n- Linear Regression\n- ML Pipelines")
    c3.markdown("**Application**\n- Streamlit\n- Plotly\n- Pandas / NumPy")

    st.markdown('<div class="section-title">Why Apache Spark?</div>', unsafe_allow_html=True)
    st.write(
        "Spark's DataFrame API and MLlib pipelines are built for distributed processing: the "
        "same code that runs here in local mode (`local[*]`, using all CPU cores on this "
        "machine) would scale to a multi-node cluster without changes, simply by pointing "
        "the SparkSession at a cluster master. This project uses Spark end-to-end — loading "
        "the CSV, cleaning it, engineering features, indexing/encoding categoricals, scaling, "
        "training, and predicting — rather than as a token import."
    )

    st.markdown('<div class="section-title">Dataset</div>', unsafe_allow_html=True)
    st.write(
        "Sample Superstore dataset (sourced from "
        "[Kaggle](https://www.kaggle.com/datasets/vivek468/superstore-dataset-final)) — a "
        "real-world US retail sales dataset with 9,994 order line items across 4 years "
        "(2014-2017), 21 original columns including Sales, Quantity, Discount, "
        "Category/Sub-Category, Segment, Region and Ship Mode."
    )

    metrics = load_metrics()
    if metrics:
        st.markdown('<div class="section-title">Current Model Snapshot</div>', unsafe_allow_html=True)
        st.json({
            "algorithm": "Linear Regression (Spark MLlib)",
            "rmse": round(metrics["rmse"], 2),
            "mae": round(metrics["mae"], 2),
            "r2": round(metrics["r2"], 3),
            "training_rows": metrics["train_rows"],
            "test_rows": metrics["test_rows"],
        })


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------
if page == "Dashboard":
    render_dashboard()
elif page == "Sales Prediction":
    render_prediction()
elif page == "Batch Prediction":
    render_batch_prediction()
elif page == "Model Performance":
    render_model_performance()
elif page == "Analytics":
    render_analytics()
elif page == "About Project":
    render_about()
