import streamlit as st
from google.cloud import bigquery
import pandas as pd
import plotly.graph_objects as go
import datetime

# Apply Custom CSS for Theme
# ---------------------------
st.markdown(
    """
    <style>
    .stApp {
        background-color: #f0f2f6;
    }
    .css-1d391kg {  /* main container */
        background-color: #f0f2f6;
    }
    h1 {
        color: #1f77b4;
        font-family: 'Arial Black', sans-serif;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------------------
# Page Configuration
# ---------------------------
st.set_page_config(page_title="Business Funnel Dashboard", layout="wide")
st.title("Business Funnel Dashboard")

# ---------------------------
# Create BigQuery Client
# ---------------------------
client = bigquery.Client()

# =====================================================
# YEARLY KPI SECTION
# =====================================================
st.subheader("Yearly KPIs")

kpi_query = """
SELECT
  year,
  total_revenue,
  total_purchases,
  active_users
FROM `event-data-pipeline-488104.event_pipeline.daily_kpis`
ORDER BY year
"""

df = client.query(kpi_query).to_dataframe()

if not df.empty:
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Revenue", f"${df['total_revenue'].sum():,.2f}")
    col2.metric("Total Purchases", int(df["total_purchases"].sum()))
    col3.metric("Active Users", int(df["active_users"].sum()))

    st.subheader("Yearly KPI Data")
    st.dataframe(df)

    # ---------------------------
    # Revenue Over Time (Last 10 Years)
    # ---------------------------
    current_year = datetime.datetime.now().year
    all_years = pd.DataFrame({"year": list(range(current_year-9, current_year+1))})

    # Merge with actual data, fill missing revenue with 0
    df_full = all_years.merge(df, on="year", how="left").fillna(0)

    st.subheader("Revenue Over Time")
    # st.line_chart(df_full.set_index("year")["total_revenue"])
    st.line_chart(df_full.set_index(df_full["year"].astype(int))["total_revenue"])

else:
    st.warning("No KPI data available.")

# =====================================================
# FUNNEL BREAKDOWN SECTION
# =====================================================
st.subheader("Funnel Breakdown")

funnel_query = """
SELECT *
FROM `event-data-pipeline-488104.event_pipeline.funnel_mart`
"""

funnel_df = client.query(funnel_query).to_dataframe()

if not funnel_df.empty:
    # Use the correct column names from BigQuery
    stages = ["Page View", "Add to Cart", "Checkout", "Purchase"]
    counts = [
        funnel_df.loc[0, "views"],
        funnel_df.loc[0, "add_to_cart"],
        funnel_df.loc[0, "checkout"],
        funnel_df.loc[0, "purchases"],
    ]

    # Plotly Funnel Chart
    fig = go.Figure(go.Funnel(
        y=stages,
        x=counts,
        textinfo="value+percent initial"
    ))
    st.plotly_chart(fig, use_container_width=True)

    # ------------------------------------------
    # Conversion Rate Calculation
    # ------------------------------------------
# Conversion Rate (capped at 100%)
views = funnel_df.loc[0, "views"]
purchases = funnel_df.loc[0, "purchases"]
conversion_rate = min((purchases / views * 100), 100) if views > 0 else 0
st.metric("Overall Conversion Rate", f"{conversion_rate:.2f}%")