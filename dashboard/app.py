import streamlit as st
from google.cloud import bigquery
import pandas as pd
import datetime

# ---------------------------
# Page Configuration
# ---------------------------
st.set_page_config(page_title="Business Funnel Dashboard", layout="wide")
st.title("Business Funnel Dashboard")

# ---------------------------
# Apply Custom CSS for Theme
# ---------------------------
st.markdown(
    """
    <style>
    /* Page background */
    .stApp {
        background-color: #f0f2f6;  /* light grey background */
    }

    /* Top header */
    .css-1v3fvcr {  /* Streamlit title container class */
        background-color: #000000;  /* black header */
        color: white;               /* white text */
        padding: 10px;
        border-radius: 5px;
    }

    /* Title font size & style */
    .css-1v3fvcr h1 {
        color: white;
        font-size: 2.5rem;
        font-family: 'Arial Black', sans-serif;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------------------
# Create BigQuery Client
# ---------------------------
# Uses credentials from environment variable GOOGLE_APPLICATION_CREDENTIALS
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

    # Revenue Over Time (Last 10 Years)
    current_year = datetime.datetime.now().year
    all_years = pd.DataFrame({"year": list(range(current_year-9, current_year+1))})
    df_full = all_years.merge(df, on="year", how="left").fillna(0)
    st.subheader("Revenue Over Time")
    st.line_chart(df_full.set_index("year")["total_revenue"])

else:
    st.warning("No KPI data available.")

# =====================================================
# FUNNEL BREAKDOWN SECTION (Simpler)
# =====================================================
st.subheader("Funnel Breakdown")

funnel_query = """
SELECT *
FROM `event-data-pipeline-488104.event_pipeline.funnel_mart`
"""

funnel_df = client.query(funnel_query).to_dataframe()

if not funnel_df.empty:
    stages = ["Page View", "Add to Cart", "Checkout", "Purchase"]
    counts = [
        funnel_df.loc[0, "views"],
        funnel_df.loc[0, "add_to_cart"],
        funnel_df.loc[0, "checkout"],
        funnel_df.loc[0, "purchases"],
    ]

    funnel_chart_df = pd.DataFrame({"Stage": stages, "Users": counts}).set_index("Stage")
    st.bar_chart(funnel_chart_df)

    # Conversion Rate
    views = funnel_df.loc[0, "views"]
    purchases = funnel_df.loc[0, "purchases"]
    conversion_rate = min((purchases / views * 100), 100) if views > 0 else 0
    st.metric("Overall Conversion Rate", f"{conversion_rate:.2f}%")