import streamlit as st
import pandas as pd

def calculate_metrics(df):
    df = df.drop_duplicates(subset=["PK_SALES_ORDER", "PRODUCT_NAME"])
    df["GROSS_TOTAL"] = df["ORDER_QUANTITY"] * df["UNIT_PRICE"]
    df["NET_TOTAL"] = df["GROSS_TOTAL"] * (1 - df["UNIT_PRICE_DISCOUNT"])
    df["LEAD_TIME_SHIPPING"] = pd.to_datetime(df["SHIP_DATE"]) - pd.to_datetime(df["ORDER_DATE"])
    df["ORDER_DELAYED"] = df["SHIP_DATE"] > df["DUE_DATE"]
    df["DISCOUNT_APPLIED"] = df["UNIT_PRICE_DISCOUNT"] > 0
    df["YEAR_MONTH"] = pd.to_datetime(df["ORDER_DATE"]).dt.to_period("M").astype(str)
    return df

# 📁 Sumário para análises
def generate_summary(df):
    return df.groupby([
        "PRODUCT_NAME", "CARD_TYPE", "SALES_REASON_NAME", "ORDER_DATE",
        "CUSTOMER_FULL_NAME", "STATUS", "CITY", "STATE_NAME", "COUNTRY_NAME"
    ], as_index=False).agg({
        "ORDER_QUANTITY": "sum",
        "GROSS_TOTAL": "sum",
        "NET_TOTAL": "sum"
    }).rename(columns={
        "ORDER_QUANTITY": "TOTAL_QUANTITY", 
        "GROSS_TOTAL": "TOTAL_GROSS_VALUE",
        "NET_TOTAL": "TOTAL_NET_VALUE"
    })