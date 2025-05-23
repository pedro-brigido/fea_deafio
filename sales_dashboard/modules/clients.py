import streamlit as st
import plotly.express as px
import pandas as pd
from utils.visuals import *
from utils.data_loader import *

def display_clients_advanced(df):
    st.markdown("## 🧍 Análise Avançada de Clientes")
    st.caption("Explore o comportamento dos principais clientes, seus padrões de compra e impactos na receita.")

    df_clients = df.copy()

    # --- KPIs ---
    client_total = df_clients.groupby("CUSTOMER_FULL_NAME")["NET_TOTAL"].sum()
    top_10 = client_total.nlargest(10)
    top_1_name = top_10.idxmax()
    top_1_value = top_10.max()
    top_10_pct = top_10.sum() / df_clients["NET_TOTAL"].sum() * 100
    freq = df_clients["PK_SALES_ORDER"].nunique() / df_clients["CUSTOMER_FULL_NAME"].nunique()

    col1, col2, col3 = st.columns(3)
    col1.metric("🏆 Cliente Top 1", top_1_name, f"${top_1_value:,.2f}")
    col2.metric("💼 % dos Top 10", f"{top_10_pct:.2f}%")
    col3.metric("📅 Freq. Média de Compra", f"{freq:.2f} pedidos/cliente")

    # --- Tabela Top 10 Clientes ---
    recent = df_clients.groupby("CUSTOMER_FULL_NAME")["ORDER_DATE"].max()
    count = df_clients.groupby("CUSTOMER_FULL_NAME")["PK_SALES_ORDER"].nunique()
    ticket = client_total / count
    df_top = pd.DataFrame({
        "Valor Total Negociado": client_total,
        "Nº de Pedidos": count,
        "Ticket Médio": ticket,
        "Última Compra": recent
    }).loc[top_10.index].sort_values(by="Valor Total Negociado", ascending=False)
    df_top.reset_index(inplace=True)
    df_top.index += 1
    df_top.insert(0, "Ranking", df_top.index)

    st.markdown("### 🧾 Top 10 Clientes por Receita")
    st.dataframe(df_top, use_container_width=True)

    # --- Análise Comportamental ---
    st.markdown("### 👤 Análise de Cliente Específico")
    selected_client = st.selectbox("📍 Selecione um cliente para análise", df_top["CUSTOMER_FULL_NAME"])
    df_sel = df_clients[df_clients["CUSTOMER_FULL_NAME"] == selected_client]

    col1, col2 = st.columns(2)
    prod_fig = px.bar(df_sel.groupby("PRODUCT_NAME")["ORDER_QUANTITY"].sum().reset_index(),
                      x="PRODUCT_NAME", y="ORDER_QUANTITY",
                      title="Produtos Mais Comprados")
    card_fig = px.pie(df_sel, names="CARD_TYPE", values="NET_TOTAL", title="Preferência de Cartão")
    col1.plotly_chart(prod_fig, use_container_width=True)
    col2.plotly_chart(card_fig, use_container_width=True)

    reason_fig = px.bar(df_sel.groupby("SALES_REASON_NAME")["NET_TOTAL"].sum().reset_index(),
                        x="SALES_REASON_NAME", y="NET_TOTAL",
                        title="Motivos de Venda Mais Comuns")
    st.plotly_chart(reason_fig, use_container_width=True)

    # --- Visão Geral de Todos os Clientes ---
    st.markdown("### 📊 Métricas Gerais por Cliente")
    general = df_clients.groupby("CUSTOMER_FULL_NAME").agg({
        "PK_SALES_ORDER": "nunique",
        "ORDER_QUANTITY": "sum",
        "NET_TOTAL": "sum"
    }).rename(columns={
        "PK_SALES_ORDER": "Pedidos",
        "ORDER_QUANTITY": "Qtd Comprada",
        "NET_TOTAL": "Total Negociado"
    })
    st.dataframe(general.sort_values("Total Negociado", ascending=False), use_container_width=True)

    # --- Download da Tabela ---
    st.download_button("⬇️ Baixar Métricas de Clientes", general.to_csv().encode("utf-8"),
                      file_name="clientes_metricas.csv", mime="text/csv")
