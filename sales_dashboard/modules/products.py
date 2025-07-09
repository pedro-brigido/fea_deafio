import streamlit as st
import plotly.express as px
import pandas as pd

def display_products_advanced(df_filtered: pd.DataFrame, df: pd.DataFrame):
    st.markdown("## 🧾 Análise Detalhada de Produtos")
    st.caption("Explore o desempenho dos produtos, impacto das promoções e diferenças regionais de ticket.")

    # KPIs
    product_summary = df_filtered.groupby("PRODUCT_NAME").agg(
        num_orders=("PK_SALES_ORDER", "nunique"),
        total_quantity_sold=("ORDER_QUANTITY", "sum"),
        gross_revenue=("GROSS_TOTAL", "sum"),
        net_revenue=("NET_TOTAL", "sum")
    ).reset_index()

    product_summary["avg_ticket_per_order"] = product_summary["net_revenue"] / product_summary["num_orders"]

    top_revenue = product_summary.sort_values("gross_revenue", ascending=False).head(1)
    top_qty = product_summary.sort_values("total_quantity_sold", ascending=False).head(1)
    top_ticket = product_summary.sort_values("avg_ticket_per_order", ascending=False).head(1)

    promo_df = df[df["SALES_REASON_NAME"] == "On Promotion"]
    promo_product = promo_df.groupby("PRODUCT_NAME")["ORDER_QUANTITY"].sum().sort_values(ascending=False).head(1)

    col1, col2, col3, col4 = st.columns([2.2, 1.4,  2.2, 2.2])
    col1.metric("💰 Produto com Maior Receita", top_revenue["PRODUCT_NAME"].values[0], f"$ {top_revenue['gross_revenue'].values[0]:,.2f}")
    col2.metric("📦 Mais Vendido (Qtd)", top_qty["PRODUCT_NAME"].values[0], f"{top_qty['total_quantity_sold'].values[0]:,}")
    col3.metric("🎯 Maior Ticket Médio", top_ticket["PRODUCT_NAME"].values[0], f"$ {top_ticket['avg_ticket_per_order'].values[0]:,.2f}")

    promo_name = promo_product.index[0] if not promo_product.empty else "-"
    promo_qty = promo_product.values[0] if not promo_product.empty else 0
    col4.metric("🎁 Destaque em Promoção", promo_name, f"{promo_qty:,}")

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🎯 Top 10 Produtos por Ticket Médio")
        top10 = product_summary.sort_values("avg_ticket_per_order", ascending=False).head(10)
        fig_top10 = px.bar(
            top10.sort_values("avg_ticket_per_order"),
            y="PRODUCT_NAME", x="avg_ticket_per_order", #orientation="h",
            text="avg_ticket_per_order", labels={"PRODUCT_NAME": "Produto", "avg_ticket_per_order": "Ticket Médio"},
            title="Top 10 Produtos por Ticket Médio"
        )
        fig_top10.update_traces(texttemplate='$ %{text:,.2f}', 
                                textposition='inside', textfont=dict(color="black", family="Arial Black", size=13))
        st.plotly_chart(fig_top10, use_container_width=True)

    with col2:
        st.markdown("### 📋 Top 10 Produtos por Receita Bruta")
        top10 = product_summary.sort_values("gross_revenue", ascending=False).head(10)
        fig_top10 = px.bar(
            top10.sort_values("gross_revenue"),
            y="PRODUCT_NAME", x="gross_revenue", #orientation="h",
            text="gross_revenue", labels={"PRODUCT_NAME": "Produto", "gross_revenue": "Receita Bruta"},
            title="Top 10 Produtos por Receita Bruta"
        )
        fig_top10.update_traces(texttemplate='$ %{text:,.2f}', 
                                textposition='inside', textfont=dict(color="black", family="Arial Black", size=13))
        st.plotly_chart(fig_top10, use_container_width=True)

    st.markdown("### 🎁 Análise de Promoções")
    if not promo_df.empty:
        promo_summary = promo_df.groupby("PRODUCT_NAME").agg(
            qtd_vendida=("ORDER_QUANTITY", "sum"),
        ).sort_values("qtd_vendida", ascending=False).head(5).reset_index()

        fig_promo = px.bar(
            promo_summary.sort_values("qtd_vendida"),
            x="qtd_vendida", y="PRODUCT_NAME", orientation="h",
            text="qtd_vendida", labels={"PRODUCT_NAME": "Produto", "qtd_vendida": "Qtd em Promoção"},
            title="Top Produtos em Promoção (por Quantidade)"
        )
        fig_promo.update_traces(texttemplate='%{text:,}', textposition='outside')
        st.plotly_chart(fig_promo, use_container_width=True)
    else:
        st.info("Nenhum dado de promoções encontrado para o período selecionado.")

    st.markdown("### 🌍 Ticket Médio por Produto e Região")
    dim = st.selectbox("Selecionar Dimensão Geográfica", ["CITY", "STATE_NAME", "COUNTRY_NAME"])
    geo_data = df_filtered.groupby(["PRODUCT_NAME", dim]).agg(
        net_revenue=("NET_TOTAL", "sum"),
        num_orders=("PK_SALES_ORDER", "nunique")
    ).reset_index()
    geo_data["ticket_medio"] = geo_data["net_revenue"] / geo_data["num_orders"]
    geo_data = geo_data.sort_values("ticket_medio", ascending=False).head(20)

    fig_geo = px.bar(
        geo_data,
        x="ticket_medio", y="PRODUCT_NAME", color=dim, orientation="h",
        text="ticket_medio",
        labels={"ticket_medio": "$", "PRODUCT_NAME": "Produto", dim: dim},
        title=f"Top Tickets Médios por Produto e {dim}"
    )
    fig_geo.update_traces(texttemplate='$ %{text:,.2f}', textposition='outside')
    st.plotly_chart(fig_geo, use_container_width=True)

    st.markdown("### 📊 Distribuição por Tipo de Cartão e Motivo de Venda")
    st.markdown("#### 🔍 Filtro: Top N Produtos por Quantidade Vendida")
    top_n = st.slider("Selecione o número de produtos para análise:", min_value=5, max_value=30, value=10, step=1)
    tab1, tab2 = st.tabs(["💳 Por Cartão", "🎯 Por Motivo"])

    top_products = (
        df.groupby("PRODUCT_NAME")["ORDER_QUANTITY"]
        .sum().nlargest(top_n).index.tolist()
    )
    df_top = df[df["PRODUCT_NAME"].isin(top_products)]

    with tab1:
        df_card = df_top.groupby(["PRODUCT_NAME", "CARD_TYPE"])["ORDER_QUANTITY"].sum().reset_index()
        card_fig = px.bar(
            df_card,
            x="ORDER_QUANTITY", y="PRODUCT_NAME", color="CARD_TYPE", orientation="h",
            barmode="group", title="💳 Vendas por Produto e Tipo de Cartão",
            labels={"PRODUCT_NAME": "Produto", "ORDER_QUANTITY": "Quantidade", "CARD_TYPE": "Tipo de Cartão"}
        )
        card_fig.update_layout(height=400 + len(df_card["PRODUCT_NAME"].unique()) * 30)
        st.plotly_chart(card_fig, use_container_width=True)

    with tab2:
        df_reason = df_top.groupby(["PRODUCT_NAME", "SALES_REASON_NAME"])["ORDER_QUANTITY"].sum().reset_index()
        reason_fig = px.bar(
            df_reason,
            x="ORDER_QUANTITY", y="PRODUCT_NAME", color="SALES_REASON_NAME", orientation="h",
            barmode="group", title="🎯 Vendas por Produto e Motivo de Venda",
            labels={"PRODUCT_NAME": "Produto", "ORDER_QUANTITY": "Quantidade", "SALES_REASON_NAME": "Motivo de Venda"}
        )
        reason_fig.update_layout(height=400 + len(df_reason["PRODUCT_NAME"].unique()) * 30)
        st.plotly_chart(reason_fig, use_container_width=True)

