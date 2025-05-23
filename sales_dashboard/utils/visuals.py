import plotly.express as px
import streamlit as st
import pandas as pd

def plot_time_series(df):
    df["YEAR_MONTH"] = pd.to_datetime(df["ORDER_DATE"]).dt.to_period("M").astype(str)
    ts = df.groupby("YEAR_MONTH")["ORDER_QUANTITY"].sum().reset_index()
    fig = px.line(ts, x="YEAR_MONTH", y="ORDER_QUANTITY", title="Evolução de Pedidos por Mês")
    st.plotly_chart(fig, use_container_width=True)

def plot_discount_analysis(df):
    df["DISCOUNT_PERCENT"] = df["UNIT_PRICE_DISCOUNT"] * 100
    fig = px.histogram(df, x="DISCOUNT_PERCENT", nbins=20, title="Distribuição de Descontos")
    st.plotly_chart(fig, use_container_width=True)

def top_products_chart(df):
    df["GROSS_TOTAL"] = df["ORDER_QUANTITY"] * df["UNIT_PRICE"]
    top = df.groupby("PRODUCT_NAME")["GROSS_TOTAL"].sum().nlargest(10).reset_index()
    fig = px.bar(top, x="PRODUCT_NAME", y="GROSS_TOTAL", title="Top 10 Produtos por Receita")
    st.plotly_chart(fig, use_container_width=True)

def product_profitability_chart(df):
    df["NET_TOTAL"] = df["ORDER_QUANTITY"] * df["UNIT_PRICE"] * (1 - df["UNIT_PRICE_DISCOUNT"])
    profitability = df.groupby("PRODUCT_NAME")["NET_TOTAL"].sum().nlargest(10).reset_index()
    fig = px.bar(profitability, x="PRODUCT_NAME", y="NET_TOTAL", title="Top 10 Produtos por Lucro")
    st.plotly_chart(fig, use_container_width=True)

def top_customers_chart(df):
    df["GROSS_TOTAL"] = df["ORDER_QUANTITY"] * df["UNIT_PRICE"]
    top = df.groupby("CUSTOMER_FULL_NAME")["GROSS_TOTAL"].sum().nlargest(10).reset_index()
    fig = px.bar(top, x="CUSTOMER_FULL_NAME", y="GROSS_TOTAL", title="Top 10 Clientes por Receita")
    st.plotly_chart(fig, use_container_width=True)

def customer_retention_chart(df):
    df["ORDER_YEAR"] = pd.to_datetime(df["ORDER_DATE"]).dt.year
    retention = df.groupby(["CUSTOMER_FULL_NAME", "ORDER_YEAR"]).size().reset_index(name="ORDERS")
    fig = px.histogram(retention, x="ORDER_YEAR", y="ORDERS", color="CUSTOMER_FULL_NAME", barmode="stack", title="Pedidos por Ano e Cliente")
    st.plotly_chart(fig, use_container_width=True)

def sales_map(df):
    df["GROSS_TOTAL"] = df["ORDER_QUANTITY"] * df["UNIT_PRICE"]
    geo = df.groupby(["CITY", "STATE_NAME", "COUNTRY_NAME"]).agg({
        "GROSS_TOTAL": "sum"
    }).reset_index()
    geo["location"] = geo["CITY"] + ", " + geo["STATE_NAME"] + ", " + geo["COUNTRY_NAME"]
    fig = px.scatter_geo(
        geo,
        locations="location",
        locationmode="country names",
        size="GROSS_TOTAL",
        hover_name="location",
        title="Mapa de Receita por Localização"
    )
    st.plotly_chart(fig, use_container_width=True)