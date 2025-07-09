import streamlit as st
import plotly.express as px
import pandas as pd

def display_kpis_general(df_filtered: pd.DataFrame, df: pd.DataFrame):
    total_orders = df_filtered["PK_SALES_ORDER"].nunique()
    total_qty = df_filtered["ORDER_QUANTITY"].sum()
    gross = df_filtered["GROSS_TOTAL"].sum()
    net = df_filtered["NET_TOTAL"].sum()
    avg_ticket_order = net / total_orders if total_orders else 0

    st.markdown("### 📌 Visão Consolidada", help="Indicadores gerais com base nos filtros selecionados")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("🧾 Pedidos", total_orders)
    col2.metric("📦 Itens Vendidos", total_qty)
    col3.metric("💰 Receita Bruta", f"${gross:,.2f}")
    col4.metric("🎯 Ticket Médio por Pedido", f"${avg_ticket_order:,.2f}")
    col5.metric("🚚 Entrega Média", f"{df_filtered['LEAD_TIME_SHIPPING'].mean().days} dias", help="Dias entre pedido e entrega")

def display_general(df_filtered: pd.DataFrame):
    st.title("📊 Painel Geral de Vendas")
    st.caption("Uma visão executiva da performance mensal de vendas e tendências ao longo do tempo.")

    df_time = df_filtered.groupby("YEAR_MONTH").agg(
        NET_TOTAL=("NET_TOTAL", "sum"),
        ORDER_QUANTITY=("ORDER_QUANTITY", "sum"),
        PK_SALES_ORDER=("PK_SALES_ORDER", "nunique")
    ).reset_index().sort_values("YEAR_MONTH")

    st.markdown("#### 🕒 Evolução Mensal")
    fig_receita_mes = px.line(
        df_time,
        x="YEAR_MONTH",
        y="NET_TOTAL",
        markers=True,
        title="📈 Receita Líquida Mensal",
        labels={"YEAR_MONTH": "Mês", "NET_TOTAL": "R$"}
    )
    fig_receita_mes.update_traces(line=dict(width=3))
    st.plotly_chart(fig_receita_mes, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        fig_volume = px.bar(
            df_time, x="YEAR_MONTH", y="ORDER_QUANTITY",
            title="📦 Quantidade Vendida por Mês",
            labels={"ORDER_QUANTITY": "Qtd. Vendida", "YEAR_MONTH": "Mês"}
        )
        st.plotly_chart(fig_volume, use_container_width=True)

    with col2:
        fig_pedidos = px.bar(
            df_time, x="YEAR_MONTH", y="PK_SALES_ORDER",
            title="🧾 Total de Pedidos por Mês",
            labels={"PK_SALES_ORDER": "Pedidos", "YEAR_MONTH": "Mês"}
        )
        st.plotly_chart(fig_pedidos, use_container_width=True)

    st.divider()
    st.markdown("#### 🔎 Destaques do Período")

    top_products = df_filtered.groupby("PRODUCT_NAME")["GROSS_TOTAL"].sum().nlargest(5).reset_index()
    top_clients = df_filtered.groupby("CUSTOMER_FULL_NAME")["GROSS_TOTAL"].sum().nlargest(5).reset_index()
    top_cities = df_filtered.groupby("CITY")["GROSS_TOTAL"].sum().nlargest(5).reset_index()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**🏆 Produtos Mais Lucrativos**")
        st.dataframe(top_products.rename(columns={"GROSS_TOTAL": "Receita"}), use_container_width=True, hide_index=True)

    with col2:
        st.markdown("**👤 Clientes Mais Lucrativos**")
        st.dataframe(top_clients.rename(columns={"GROSS_TOTAL": "Receita"}), use_container_width=True, hide_index=True)

    with col3:
        st.markdown("**🌍 Cidades com Maior Receita**")
        st.dataframe(top_cities.rename(columns={"GROSS_TOTAL": "Receita"}), use_container_width=True, hide_index=True)

    st.info("💡 Explore detalhes por produto, cliente e localização nas abas específicas para análises aprofundadas.")
