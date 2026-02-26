import streamlit as st
from google.cloud import bigquery
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(page_title="Executive E-Commerce Dashboard", layout="wide")

# --------------------------------------------------
# DARK THEME + WIDGET FIX CSS
# --------------------------------------------------
st.markdown("""
<style>

/* GLOBAL */
.block-container { padding-top: 2.5rem !important; }

.stApp {
    background: linear-gradient(135deg, #0f172a, #111827);
    color: white;
}

/* TITLE */
.dashboard-title {
    font-size: 42px;
    font-weight: 700;
    color: white;
}
.dashboard-subtitle {
    font-size: 16px;
    color: white;
    margin-bottom: 25px;
}

/* KPI CARDS */
.metric-card {
    background: linear-gradient(135deg,#7c3aed,#06b6d4);
    padding: 20px;
    border-radius: 20px;
    text-align: center;
}
.metric-title { font-size: 14px; color: white; }
.metric-value { font-size: 30px; font-weight: 600; color: white; }

/* SELECTBOX */
/* Radio group label (Select View) */
div[data-testid="stRadio"] > label {
    color: white !important;
    font-weight: 600 !important;
}

/* Radio option wrapper */
div[data-testid="stRadio"] div[role="radiogroup"] label {
    color: white !important;
    font-weight: 500 !important;
}

/* Radio option text (deep override) */
div[data-testid="stRadio"] div[role="radiogroup"] label div {
    color: white !important;
}

/* Ensure span text is white */
div[data-testid="stRadio"] span {
    color: white !important;
}

/* Radio circle border */
div[data-testid="stRadio"] input[type="radio"] + div {
    border-color: white !important;
}
div[data-testid="stSelectbox"] > label {
    color: white !important;
    font-weight: 600 !important;
}


/* CHART TITLE */
.chart-title {
    font-size: 20px;
    font-weight: 600;
    color: white;
    margin-top: 20px;
    margin-bottom: 15px;
}

</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# TITLE SECTION
# --------------------------------------------------
st.markdown("""
<div class="dashboard-title">
Event-Driven E-Commerce Analytics
</div>
<div class="dashboard-subtitle">
This dashboard analyzes event-driven e-commerce data processed through a Python-based pipeline and stored in BigQuery.
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------
# BIGQUERY CONNECTION
# --------------------------------------------------
key_path = os.path.join(os.path.dirname(__file__), "../credentials/key.json")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_path
client = bigquery.Client()

# --------------------------------------------------
# FETCH YEARS
# --------------------------------------------------
year_query = """
SELECT DISTINCT EXTRACT(YEAR FROM event_timestamp) as year
FROM `event-data-pipeline-488104.event_pipeline.fact_events`
ORDER BY year
"""
year_df = client.query(year_query).to_dataframe()
years = sorted(year_df["year"].dropna().astype(int).tolist()) if not year_df.empty else []

# --------------------------------------------------
# FILTERS
# --------------------------------------------------
col1, col2 = st.columns([1,2])

with col1:
    selected_year = st.selectbox("Select Year", ["All"] + years)

with col2:
    chart_type = st.radio(
        "Select View",
        [
            "Revenue",
            "Sales Funnel",
            "Event Distribution",
            "Customer Engagement",
            "Weekly Orders"
        ],
        horizontal=True
    )

# --------------------------------------------------
# KPI QUERY
# --------------------------------------------------
kpi_query = """
SELECT 
    ROUND(SUM(price),2) as gmv,
    ROUND(SUM(CASE WHEN event_type='purchase' THEN price END),2) as revenue,
    COUNTIF(event_type='purchase') as total_orders,
    COUNT(DISTINCT user_id) as active_users
FROM `event-data-pipeline-488104.event_pipeline.fact_events`
"""
if selected_year != "All":
    kpi_query += f" WHERE EXTRACT(YEAR FROM event_timestamp) = {selected_year}"

kpi_df = client.query(kpi_query).to_dataframe()

if not kpi_df.empty:
    total_gmv = kpi_df["gmv"].iloc[0] or 0
    total_revenue = kpi_df["revenue"].iloc[0] or 0
    total_orders = kpi_df["total_orders"].iloc[0] or 0
    total_users = kpi_df["active_users"].iloc[0] or 0
    avg_order_value = round(total_revenue / total_orders, 2) if total_orders > 0 else 0

    cols = st.columns(5)
    kpis = [
        ("GMV", f"${total_gmv:,.0f}"),
        ("Net Revenue", f"${total_revenue:,.0f}"),
        ("Orders", f"{int(total_orders):,}"),
        ("Users", f"{int(total_users):,}"),
        ("Avg Order", f"${avg_order_value:,.0f}")
    ]

    for col, (title, value) in zip(cols, kpis):
        col.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">{title}</div>
            <div class="metric-value">{value}</div>
        </div>
        """, unsafe_allow_html=True)

# --------------------------------------------------
# CHARTS
# --------------------------------------------------

# REVENUE
if chart_type == "Revenue":

    st.markdown('<div class="chart-title">Revenue Trend (Monthly)</div>', unsafe_allow_html=True)

    query = """
    SELECT DATE_TRUNC(event_timestamp, MONTH) AS month_date,
           ROUND(SUM(price),2) AS revenue
    FROM `event-data-pipeline-488104.event_pipeline.fact_events`
    WHERE event_type='purchase'
    """
    if selected_year != "All":
        query += f" AND EXTRACT(YEAR FROM event_timestamp) = {selected_year}"
    query += " GROUP BY month_date ORDER BY month_date"

    df = client.query(query).to_dataframe()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["month_date"],
        y=df["revenue"],
        mode="lines+markers",
        fill="tozeroy",
        line=dict(color="#38bdf8", width=3)
    ))
    fig.update_layout(height=380, plot_bgcolor="#1e293b",
                      paper_bgcolor="#1e293b", font=dict(color="white"))
    st.plotly_chart(fig, use_container_width=True)

# SALES FUNNEL
elif chart_type == "Sales Funnel":

    st.markdown('<div class="chart-title">Sales Funnel</div>', unsafe_allow_html=True)

    query = """
    SELECT 
        COUNTIF(event_type='page_view') as views,
        COUNTIF(event_type='add_to_cart') as add_to_cart,
        COUNTIF(event_type='checkout') as checkout,
        COUNTIF(event_type='purchase') as purchases
    FROM `event-data-pipeline-488104.event_pipeline.fact_events`
    """
    if selected_year != "All":
        query += f" WHERE EXTRACT(YEAR FROM event_timestamp) = {selected_year}"

    df = client.query(query).to_dataframe()

    values = df.iloc[0].tolist()
    stages = ["Page View", "Add to Cart", "Checkout", "Purchase"]

    fig = go.Figure(go.Funnel(
        y=stages,
        x=values,
        textinfo="value+percent initial",
        textfont=dict(color="white"),
        marker=dict(color=["#38bdf8","#0ea5e9","#2563eb","#1d4ed8"])
    ))

    fig.update_layout(height=420, plot_bgcolor="#1e293b",
                      paper_bgcolor="#1e293b", font=dict(color="white"))
    st.plotly_chart(fig, use_container_width=True)

# EVENT DISTRIBUTION
elif chart_type == "Event Distribution":

    st.markdown('<div class="chart-title">Event Distribution</div>', unsafe_allow_html=True)

    query = """
    SELECT event_type, COUNT(*) as total
    FROM `event-data-pipeline-488104.event_pipeline.fact_events`
    """
    if selected_year != "All":
        query += f" WHERE EXTRACT(YEAR FROM event_timestamp) = {selected_year}"
    query += " GROUP BY event_type"

    df = client.query(query).to_dataframe()

    fig = px.pie(df, names="event_type", values="total", hole=0.6)
    fig.update_layout(height=380, plot_bgcolor="#1e293b",
                      paper_bgcolor="#1e293b", font=dict(color="white"))
    st.plotly_chart(fig, use_container_width=True)

# CUSTOMER ENGAGEMENT
elif chart_type == "Customer Engagement":

    st.markdown('<div class="chart-title">Customer Engagement (Daily Active Users)</div>', unsafe_allow_html=True)

    query = """
    SELECT DATE(event_timestamp) as date,
           COUNT(DISTINCT user_id) as users
    FROM `event-data-pipeline-488104.event_pipeline.fact_events`
    """
    if selected_year != "All":
        query += f" WHERE EXTRACT(YEAR FROM event_timestamp) = {selected_year}"
    query += " GROUP BY date ORDER BY date"

    df = client.query(query).to_dataframe()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["date"],
        y=df["users"],
        mode="lines",
        fill="tozeroy",
        line=dict(color="#0ea5e9", width=3)
    ))
    fig.update_layout(height=400, plot_bgcolor="#1e293b",
                      paper_bgcolor="#1e293b", font=dict(color="white"))
    st.plotly_chart(fig, use_container_width=True)

# WEEKLY ORDERS
elif chart_type == "Weekly Orders":

    st.markdown('<div class="chart-title">Weekly Orders</div>', unsafe_allow_html=True)

    query = """
    SELECT DATE_TRUNC(event_timestamp, WEEK) as week,
           COUNTIF(event_type='purchase') as orders
    FROM `event-data-pipeline-488104.event_pipeline.fact_events`
    """
    if selected_year != "All":
        query += f" WHERE EXTRACT(YEAR FROM event_timestamp) = {selected_year}"
    query += " GROUP BY week ORDER BY week"

    df = client.query(query).to_dataframe()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["week"],
        y=df["orders"],
        marker=dict(color="#2563eb")
    ))
    fig.update_layout(height=400, plot_bgcolor="#1e293b",
                      paper_bgcolor="#1e293b", font=dict(color="white"))
    st.plotly_chart(fig, use_container_width=True)