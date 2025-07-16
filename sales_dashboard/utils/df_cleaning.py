import streamlit as st
import pandas as pd

def dedup_and_cast_df(df):
    df = df.drop_duplicates(subset=["PK_SALES_ORDER", "PRODUCT_NAME"])
    df["YEAR_MONTH"] = pd.to_datetime(df["YEAR_MONTH"]).dt.to_period("M").astype(str)
    df["YEAR"] = pd.to_datetime(df["ORDER_YEAR"]).dt.year
    return df