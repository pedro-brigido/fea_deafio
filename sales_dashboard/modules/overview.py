import streamlit as st
import plotly.express as px
import pandas as pd
from utils.visuals import *
from utils.data_loader import *

def display_kpis_general(df_filtered: pd.DataFrame, df: pd.DataFrame):
    total_orders = df_filtered["PK_SALES_ORDER"].nunique()
    total_qty = df_filtered["ORDER_QUANTITY"].sum()
    gross = df_filtered["GROSS_TOTAL"].sum()
    net = df_filtered["NET_TOTAL"].sum()
    avg_ticket_order = net / total_orders if total_orders else 0

    st.markdown("### 📌 Indicadores Gerais")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("🧾 Total de Pedidos", total_orders)
    col2.metric("📦 Quantidade Vendida", total_qty)
    col3.metric("💰 Receita Bruta", f"${gross:,.2f}")
    col4.metric("🎯 Ticket Médio / Pedido", f"${avg_ticket_order:,.2f}")
    col5.metric("📅 Tempo Médio de Entrega", f"{df_filtered['LEAD_TIME_SHIPPING'].mean().days} dias")

def display_general(df_combined: pd.DataFrame):
    st.title("📊 Visão Geral da Performance de Vendas")
    st.caption("📅 Acompanhe o desempenho mensal de vendas, produtos e clientes.")

    df_time = df_combined.groupby("YEAR_MONTH").agg({
        "NET_TOTAL": "sum",
        "ORDER_QUANTITY": "sum",
        "PK_SALES_ORDER": "nunique",
        "GROSS_TOTAL": "sum"
    }).reset_index()

    fig = px.line(
        df_time,
        x="YEAR_MONTH",
        y="NET_TOTAL",
        markers=True,
        title="📈 Receita Líquida por Mês",
        labels={"YEAR_MONTH": "Mês", "NET_TOTAL": "Receita (R$)"}
    )
    fig.update_traces(line=dict(width=3))
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    col1.plotly_chart(px.line(df_time, x="YEAR_MONTH", y="ORDER_QUANTITY", title="📦 Volume Vendido por Mês"), use_container_width=True)
    col2.plotly_chart(px.line(df_time, x="YEAR_MONTH", y="PK_SALES_ORDER", title="🧾 Pedidos por Mês"), use_container_width=True)

    with st.expander("📦 Top Produtos por Receita"):
        top_products = df_combined.groupby("PRODUCT_NAME")["GROSS_TOTAL"].sum().nlargest(10).reset_index()
        # st.dataframe(top_products)
        st.bar_chart(top_products, x="PRODUCT_NAME", y="GROSS_TOTAL", use_container_width=True, height=500, width=1000, y_label="Receita (R$)", x_label="Produtos")

    with st.expander("💼 Top Clientes por Receita"):
        top_clients = df_combined.groupby("CUSTOMER_FULL_NAME")["GROSS_TOTAL"].sum().nlargest(10).reset_index()
        # st.dataframe(top_clients)
        st.bar_chart(top_clients, x="CUSTOMER_FULL_NAME", y="GROSS_TOTAL", use_container_width=True, height=500, width=1000)

    with st.expander("🌆 Top Cidades por Receita"):
        top_cities = df_combined.groupby("CITY")["GROSS_TOTAL"].sum().nlargest(10).reset_index()
        # st.dataframe(top_cities)
        st.bar_chart(top_cities, x="CITY", y="GROSS_TOTAL")
