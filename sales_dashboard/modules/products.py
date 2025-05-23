import streamlit as st
import plotly.express as px
import pandas as pd
from utils.visuals import *
from utils.data_loader import *

def display_products_advanced(df):
    st.markdown("## 🧾 Análise Profunda dos Produtos")
    st.caption("Explore a performance individual de cada produto, seu impacto nas vendas e promoções.")

    # --- KPIs ---
    total_orders = df["PK_SALES_ORDER"].nunique()
    total_qty = df["ORDER_QUANTITY"].sum()
    product_revenue = df.groupby("PRODUCT_NAME")["GROSS_TOTAL"].sum()
    product_qty = df.groupby("PRODUCT_NAME")["ORDER_QUANTITY"].sum()
    product_ticket = df.groupby("PRODUCT_NAME").apply(
        lambda x: (x["GROSS_TOTAL"].sum() - (x["GROSS_TOTAL"] * x["UNIT_PRICE_DISCOUNT"]).sum()) / x["PK_SALES_ORDER"].nunique()
    ).sort_values(ascending=False)
    avg_ticket_item = df["GROSS_TOTAL"].sum() / df["ORDER_QUANTITY"].sum()

    top_promo_df = df[df["SALES_REASON_NAME"] == "On Promotion"]
    if not top_promo_df.empty:
        promo_product = top_promo_df.groupby("PRODUCT_NAME")["ORDER_QUANTITY"].sum().idxmax()
        promo_qty = top_promo_df.groupby("PRODUCT_NAME")["ORDER_QUANTITY"].sum().max()
    else:
        promo_product, promo_qty = "-", 0

    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Produto com Maior Receita", product_revenue.idxmax(), f"${product_revenue.max():,.2f}")
    col2.metric("📦 Produto Mais Vendido (Qtd)", product_qty.idxmax(), int(product_qty.max()))
    col3.metric("🎯 Maior Ticket Médio", product_ticket.index[0], f"${product_ticket.iloc[0]:,.2f}")

    col4, col5 = st.columns(2)
    col4.metric("🎁 Produto em Promoção com Mais Vendas", promo_product, int(promo_qty))
    col5.metric("🪙 Ticket Médio por Item", f"${avg_ticket_item:,.2f}")

    # --- Tabela e Ranking ---
    st.markdown("### 📋 Ranking de Produtos por Receita")
    product_table = df.groupby("PRODUCT_NAME").agg({
        "PK_SALES_ORDER": "nunique",
        "ORDER_QUANTITY": "sum",
        "GROSS_TOTAL": "sum",
        "NET_TOTAL": "sum"
    }).rename(columns={
        "PK_SALES_ORDER": "Nº de Pedidos",
        "ORDER_QUANTITY": "Quantidade Comprada",
        "GROSS_TOTAL": "Valor Bruto",
        "NET_TOTAL": "Valor Líquido"
    })
    product_table["Ticket Médio"] = product_table["Valor Líquido"] / product_table["Nº de Pedidos"]

    df_sorted = product_table.sort_values("Valor Bruto", ascending=False).head(10).reset_index()
    st.plotly_chart(
        px.bar(df_sorted, x="Valor Bruto", y="PRODUCT_NAME", orientation="h", title="Top 10 Produtos por Receita"),
        use_container_width=True
    )

    # --- Promoções ---
    st.markdown("### 🎁 Análise de Produtos em Promoção")
    if not top_promo_df.empty:
        top_promo = top_promo_df.groupby("PRODUCT_NAME")["ORDER_QUANTITY"].sum().nlargest(5).reset_index()
        st.plotly_chart(
            px.bar(top_promo, x="ORDER_QUANTITY", y="PRODUCT_NAME", orientation="h", title="Top Produtos em Promoções"),
            use_container_width=True
        )
    else:
        st.info("Nenhum dado de promoção encontrado para o período selecionado.")

    # --- Geografia ---
    st.markdown("### 🌍 Ticket Médio por Produto e Localidade")
    dim = st.selectbox("Selecionar dimensão:", ["CITY", "STATE_NAME", "COUNTRY_NAME"])
    geo_group = df.groupby(["PRODUCT_NAME", dim])["NET_TOTAL"].sum() / df.groupby(["PRODUCT_NAME", dim])["PK_SALES_ORDER"].nunique()
    geo_df = geo_group.reset_index(name="Ticket Médio")
    geo_df = geo_df.sort_values("Ticket Médio", ascending=False).head(20)
    st.plotly_chart(
        px.bar(geo_df, x="Ticket Médio", y="PRODUCT_NAME", color=dim, orientation="h",
               title="Ticket Médio por Produto e Localidade"),
        use_container_width=True
    )

    # --- Cartão e Motivo ---
    st.markdown("### 📊 Distribuição por Tipo de Cartão e Motivo de Venda")
    tab1, tab2 = st.tabs(["💳 Por Cartão", "🎯 Por Motivo"])

    with tab1:
        card_fig = px.bar(
            df.groupby(["PRODUCT_NAME", "CARD_TYPE"])["ORDER_QUANTITY"].sum().reset_index(),
            x="ORDER_QUANTITY", y="PRODUCT_NAME", color="CARD_TYPE", orientation="h",
            title="Vendas por Produto e Tipo de Cartão")
        st.plotly_chart(card_fig, use_container_width=True)

    with tab2:
        reason_fig = px.bar(
            df.groupby(["PRODUCT_NAME", "SALES_REASON_NAME"])["ORDER_QUANTITY"].sum().reset_index(),
            x="ORDER_QUANTITY", y="PRODUCT_NAME", color="SALES_REASON_NAME", orientation="h",
            title="Vendas por Produto e Motivo de Venda")
        st.plotly_chart(reason_fig, use_container_width=True)

    # --- Download da Tabela ---
    st.download_button("⬇️ Baixar Tabela de Produtos", product_table.to_csv().encode("utf-8"), file_name="produtos.csv", mime="text/csv")
