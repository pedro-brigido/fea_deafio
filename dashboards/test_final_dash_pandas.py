import streamlit as st
import plotly.express as px
import pandas as pd
import snowflake.connector as sc
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Streamlit app setup
st.set_page_config(page_title="Snowflake Dashboard", layout="wide")

# Snowflake credentials
snowflake_creds = {
    "account": os.getenv("DEV_SNOWFLAKE_ACCOUNT"),
    "database": "FEA24_11",
    "schema": "RAW_ADVENTURE_WORKS",
    "warehouse": os.getenv("DEV_SNOWFLAKE_WAREHOUSE"),
    "role": os.getenv("DEV_SNOWFLAKE_ROLE"),
    "user": os.getenv("DEV_SNOWFLAKE_USER"),
    "password": os.getenv("DEV_SNOWFLAKE_PASSWORD"),
}

def get_combined_data(schema="CEA_PBRIGIDO_MARTS", database="FEA24_11"):
    """Fetch combined data from Snowflake with all necessary joins."""
    query = f"""
    SELECT
        fso.*, 
        dp.PRODUCT_NAME,
        dcc.CARD_TYPE,
        dsr.SALES_REASON_NAME,
        dc.CUSTOMER_FULL_NAME,
        da.CITY, da.STATE_NAME, da.COUNTRY_NAME
    FROM {database}.{schema}.FCT_SALES_ORDERS fso
    LEFT JOIN {database}.{schema}.DIM_PRODUCTS dp ON fso.FK_PRODUCT = dp.PK_PRODUCT
    LEFT JOIN {database}.{schema}.DIM_CREDIT_CARD dcc ON fso.FK_CREDIT_CARD = dcc.PK_CREDIT_CARD
    LEFT JOIN {database}.{schema}.DIM_SALES_REASON dsr ON fso.PK_SALES_ORDER = dsr.PK_SALES_ORDER
    LEFT JOIN {database}.{schema}.DIM_CUSTOMER dc ON fso.FK_CUSTOMER = dc.PK_CUSTOMER
    LEFT JOIN {database}.{schema}.DIM_ADRESS da ON fso.FK_SHIP_TO_ADDRESS = da.PK_ADDRESS
    """
    try:
        with sc.connect(**snowflake_creds) as conn:
            return pd.read_sql(query, conn)
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

def calculate_metrics(df):
    """Deduplicate and calculate additional metrics for sales orders."""
    df = df.drop_duplicates(subset=["PK_SALES_ORDER", "PRODUCT_NAME"])
    df["GROSS_TOTAL"] = df["ORDER_QUANTITY"] * df["UNIT_PRICE"]
    df["NET_TOTAL"] = df["GROSS_TOTAL"] * (1 - df["UNIT_PRICE_DISCOUNT"])
    df["LEAD_TIME_SHIPPING"] = pd.to_datetime(df["SHIP_DATE"]) - pd.to_datetime(df["ORDER_DATE"])
    df["ORDER_DELAYED"] = df["SHIP_DATE"] > df["DUE_DATE"]
    df["DISCOUNT_APPLIED"] = df["UNIT_PRICE_DISCOUNT"] > 0
    return df

def display_metrics(df):
    """Display summarized metrics in the Streamlit dashboard."""
    summarized_df = pd.DataFrame({
        "TOTAL_ORDERS": [df["PK_SALES_ORDER"].nunique()],
        "QUANTITY_PURCHASED": [df["ORDER_QUANTITY"].sum()],
        "TOTAL_GROSS_VALUE": [df["GROSS_TOTAL"].sum()],
        "TOTAL_NET_VALUE": [df["NET_TOTAL"].sum()],
        "AVERAGE_TICKET": [df["NET_TOTAL"].sum() / df["PK_SALES_ORDER"].nunique()]
    })

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Orders", summarized_df["TOTAL_ORDERS"].iloc[0])
    col2.metric("Total Quantity Purchased", summarized_df["QUANTITY_PURCHASED"].iloc[0])
    col3.metric("Total Sales (Gross)", f"${summarized_df['TOTAL_GROSS_VALUE'].iloc[0]:,.2f}")
    col4.metric("Total Sales (Net)", f"${summarized_df['TOTAL_NET_VALUE'].iloc[0]:,.2f}")
    col5.metric("Average Ticket", f"${summarized_df['AVERAGE_TICKET'].iloc[0]:,.2f}")

    # Custom line chart: NET_TOTAL, TOTAL_ORDERS, TOTAL_QUANTITY over time
    df_time = df.copy()
    df_time["ORDER_DATE"] = pd.to_datetime(df_time["ORDER_DATE"])
    df_time["YEAR_MONTH"] = df_time["ORDER_DATE"].dt.to_period("M").astype(str)
    df_time = df_time.groupby("YEAR_MONTH").agg({
        "GROSS_TOTAL": "sum",
        "ORDER_QUANTITY": "sum",
        "CUSTOMER_FULL_NAME": "count"  # Proxy for total orders
    }).rename(columns={
        "GROSS_TOTAL": "Total Net Revenue",
        "ORDER_QUANTITY": "Total Quantity",
        "CUSTOMER_FULL_NAME": "Total Orders"
    }).reset_index()

    fig_revenue = px.line(
        df_time,
        x="YEAR_MONTH",
        y="Total Net Revenue",
        title="📈 Net Revenue Over Time",
        markers=True
    )
    st.plotly_chart(fig_revenue, use_container_width=True)

    fig_quantity = px.line(
        df_time,
        x="YEAR_MONTH",
        y="Total Quantity",
        title="📦 Quantity Sold Over Time",
        markers=True
    )
    st.plotly_chart(fig_quantity, use_container_width=True)

    fig_orders = px.line(
        df_time,
        x="YEAR_MONTH",
        y="Total Orders",
        title="🧾 Orders Over Time",
        markers=True
    )
    st.plotly_chart(fig_orders, use_container_width=True)


def generate_summary(df):
    """Generate summary DataFrame for visualization."""
    return df.groupby([
        "PRODUCT_NAME", "CARD_TYPE", "SALES_REASON_NAME", "ORDER_DATE",
        "CUSTOMER_FULL_NAME", "STATUS", "CITY", "STATE_NAME", "COUNTRY_NAME"
    ], as_index=False).agg({
        "ORDER_QUANTITY": "sum",
        "GROSS_TOTAL": "sum"
    }).rename(columns={"ORDER_QUANTITY": "TOTAL_QUANTITY", "GROSS_TOTAL": "TOTAL_GROSS_VALUE"})

def display_charts(df_summary):
    """Render charts for the dashboard."""

    df_summary["ORDER_DATE"] = pd.to_datetime(df_summary["ORDER_DATE"])

    date_range = st.sidebar.date_input("Select Date Range", [df_summary["ORDER_DATE"].min(), df_summary["ORDER_DATE"].max()])

    if len(date_range) == 2:
        df_summary = df_summary[(df_summary["ORDER_DATE"] >= pd.to_datetime(date_range[0])) & (df_summary["ORDER_DATE"] <= pd.to_datetime(date_range[1]))]

    with st.expander("📦 Top 5 Products by Gross Sales"):
        top_products = df_summary.groupby("PRODUCT_NAME")["TOTAL_GROSS_VALUE"].sum().nlargest(5).reset_index()
        st.dataframe(top_products)

    with st.expander("👤 Top 5 Customers by Gross Sales"):
        top_customers = df_summary.groupby("CUSTOMER_FULL_NAME")["TOTAL_GROSS_VALUE"].sum().nlargest(5).reset_index()
        st.dataframe(top_customers)

    with st.expander("🌆 Top 5 Cities by Gross Sales"):
        top_cities = df_summary.groupby("CITY")["TOTAL_GROSS_VALUE"].sum().nlargest(5).reset_index()
        st.dataframe(top_cities)

    with st.expander("📈 Top 3 Sales Reasons"):
        top_reasons = df_summary.groupby("SALES_REASON_NAME")["TOTAL_GROSS_VALUE"].sum().nlargest(3).reset_index()
        st.dataframe(top_reasons)

    fig = px.bar(
        df_summary,
        x="PRODUCT_NAME",
        y="TOTAL_GROSS_VALUE",
        labels={"x": "Product", "y": "Total Sales Value"},
        title="Total Sales by Product",
        color="TOTAL_GROSS_VALUE"
    )
    st.plotly_chart(fig, use_container_width=True)

    fig_card = px.bar(
        df_summary,
        x="CARD_TYPE",
        y="TOTAL_GROSS_VALUE",
        title="Sales Distribution by Card Type"
    )
    st.plotly_chart(fig_card, use_container_width=True)


# Sidebar button to load data
if "df_combined" not in st.session_state:
    st.session_state.df_combined = None

if st.sidebar.button("Load Data"):
    st.session_state.df_combined = get_combined_data()

if st.session_state.df_combined is not None:
    df_combined = calculate_metrics(st.session_state.df_combined)
    display_metrics(df_combined)

    df_summary = generate_summary(df_combined)
    display_charts(df_summary)

st.title("📊 Sales Performance Dashboard")
st.caption("Developed for the BI challenge using Streamlit and Snowflake")

# Sidebar button to load data
if "df_combined" not in st.session_state:
    st.session_state.df_combined = None

if st.sidebar.button("Load Data"):
    st.session_state.df_combined = get_combined_data()

if st.session_state.df_combined is not None:
    df_combined = calculate_metrics(st.session_state.df_combined)
    display_metrics(df_combined)

    df_summary = generate_summary(df_combined)
    display_charts(df_summary)

st.title("📊 Sales Performance Dashboard")
st.caption("Developed for the BI challenge using Streamlit and Snowflake")
