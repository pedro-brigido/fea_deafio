# 📦 Imports
import streamlit as st
import plotly.express as px
import pandas as pd
import snowflake.connector as sc
import os
import time
from dotenv import load_dotenv

# 🔐 Carregar variáveis de ambiente
load_dotenv()

# ⚙️ Configurações da aplicação
st.set_page_config(page_title="📊 Sales Performance Dashboard", layout="wide")

# 🔑 Credenciais Snowflake
snowflake_creds = {
    "account": os.getenv("DEV_SNOWFLAKE_ACCOUNT"),
    "database": "FEA24_11",
    "schema": "RAW_ADVENTURE_WORKS",
    "warehouse": os.getenv("DEV_SNOWFLAKE_WAREHOUSE"),
    "role": os.getenv("DEV_SNOWFLAKE_ROLE"),
    "user": os.getenv("DEV_SNOWFLAKE_USER"),
    "password": os.getenv("DEV_SNOWFLAKE_PASSWORD"),
}

# 📥 Consulta e cache de dados
@st.cache_data(ttl="1h")
def get_combined_data(schema="CEA_PBRIGIDO_MARTS", database="FEA24_11"):
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
        st.error(f"Erro ao buscar dados: {e}")
        return None

# 📊 Processamento e métricas
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

# 📈 KPIs
def display_kpis_general(df_filtered, df):
    total_orders = df_filtered["PK_SALES_ORDER"].nunique()
    total_qty = df_filtered["ORDER_QUANTITY"].sum()
    gross = df_filtered["GROSS_TOTAL"].sum()
    net = df_filtered["NET_TOTAL"].sum()
    avg_ticket_order = net / total_orders if total_orders else 0
    avg_ticket_item = net / total_qty if total_qty else 0
    current_period_clients = df_filtered["CUSTOMER_FULL_NAME"].unique()
    previous_period_clients = df[df["ORDER_DATE"] < df_filtered["ORDER_DATE"].min()]["CUSTOMER_FULL_NAME"].unique()
    new_clients_in_period = len([client for client in current_period_clients if client not in previous_period_clients])

    st.markdown("### 📌 Indicadores Gerais")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("🧾 Total de Pedidos", total_orders)
    col2.metric("📦 Quantidade Vendida", total_qty)
    col3.metric("💰 Receita Bruta", f"${gross:,.2f}")
    col4.metric("🎯 Ticket Médio / Pedido", f"${avg_ticket_order:,.2f}")
    # col5.metric("🪙 Ticket Médio / Item", f"${avg_ticket_item:,.2f}")
    col5.metric("📅 Tempo Médio de Entrega", f"{df_filtered['LEAD_TIME_SHIPPING'].mean().days} dias")
    # col6.metric("👥 Clientes Novos", new_clients_in_period)

# 📊 Visuais e Filtros
def display_filters(df):
    st.sidebar.header("🎛️ Filtros")
    df["ORDER_DATE"] = pd.to_datetime(df["ORDER_DATE"])

    date_range = st.sidebar.date_input("Período", [df["ORDER_DATE"].min(), df["ORDER_DATE"].max()])
    product_filter = st.sidebar.multiselect("Produto", df["PRODUCT_NAME"].unique())
    card_type_filter = st.sidebar.multiselect("Tipo de Cartão", df["CARD_TYPE"].unique())
    city_filter = st.sidebar.multiselect("Cidade", df["CITY"].unique())
    state_filter = st.sidebar.multiselect("Estado", df["STATE_NAME"].unique())
    country_filter = st.sidebar.multiselect("País", df["COUNTRY_NAME"].unique())

    df_filtered = df.copy()
    if len(date_range) == 2:
        df_filtered = df_filtered[
            (df_filtered["ORDER_DATE"] >= pd.to_datetime(date_range[0])) &
            (df_filtered["ORDER_DATE"] <= pd.to_datetime(date_range[1]))
        ]
    if product_filter:
        df_filtered = df_filtered[df_filtered["PRODUCT_NAME"].isin(product_filter)]
    if card_type_filter:
        df_filtered = df_filtered[df_filtered["CARD_TYPE"].isin(card_type_filter)]
    if city_filter:
        df_filtered = df_filtered[df_filtered["CITY"].isin(city_filter)]
    if state_filter:
        df_filtered = df_filtered[df_filtered["STATE_NAME"].isin(state_filter)]
    if country_filter:
        df_filtered = df_filtered[df_filtered["COUNTRY_NAME"].isin(country_filter)]

    return df_filtered

def display_general(df_summary, df_combined):
    st.markdown("### 📊 Visuais de Desempenho")

    df_time = df_combined.groupby("YEAR_MONTH").agg({
        "NET_TOTAL": "sum",
        "ORDER_QUANTITY": "sum",
        "PK_SALES_ORDER": "nunique",
        "GROSS_TOTAL": "sum"
    }).reset_index()

    
    st.plotly_chart(px.line(df_time, x="YEAR_MONTH", y="NET_TOTAL", title="📈 Receita Líquida Mensal"), use_container_width=True)

    
    col1, col2 = st.columns(2)
    col1.plotly_chart(px.line(df_time, x="YEAR_MONTH", y="ORDER_QUANTITY", title="📦 Volume Vendido por Mês"), use_container_width=True)
    col2.plotly_chart(px.line(df_time, x="YEAR_MONTH", y="PK_SALES_ORDER", title="🧾 Pedidos por Mês"), use_container_width=True)

    with st.expander("📦 Top Produtos por Receita"):
        top_products = df_summary.groupby("PRODUCT_NAME")["TOTAL_GROSS_VALUE"].sum().nlargest(5).reset_index()
        st.dataframe(top_products)

    with st.expander("💼 Top Clientes por Receita"):
        top_clients = df_summary.groupby("CUSTOMER_FULL_NAME")["TOTAL_GROSS_VALUE"].sum().nlargest(10).reset_index()
        st.dataframe(top_clients)

    with st.expander("🌆 Top Cidades por Receita"):
        top_cities = df_summary.groupby("CITY")["TOTAL_GROSS_VALUE"].sum().nlargest(5).reset_index()
        st.dataframe(top_cities)

def display_kpis_products(df_filtered):
    st.markdown("### 📊 Indicadores por Produto")
    best_product_by_revenue = df_filtered.groupby("PRODUCT_NAME")["GROSS_TOTAL"].sum().nlargest(1).index[0]
    best_product_by_quantity = df_filtered.groupby("PRODUCT_NAME")["ORDER_QUANTITY"].sum().nlargest(1).index[0]
    total_orders = df_filtered["PK_SALES_ORDER"].nunique()
    total_qty = df_filtered["ORDER_QUANTITY"].sum()
    avg_ticket_order = df_filtered["GROSS_TOTAL"].sum() / df_filtered["PK_SALES_ORDER"].nunique()
    avg_ticket_item = df_filtered["GROSS_TOTAL"].sum() / df_filtered["ORDER_QUANTITY"].sum()
    greater_average_ticket = df_filtered.groupby("PRODUCT_NAME")["GROSS_TOTAL"].sum().nlargest(1).index[0]

    col1, col2, col3, col4, col5 = st.columns(5)
    
    col1.metric("🎯 Melhor produto em receita", best_product_by_revenue)
    col2.metric("🪙 Melhor produto em quantidade vendida", best_product_by_quantity)
    col3.metric("📦 Total pedidos/total produtos vendidos", f"{total_orders}/{total_qty}")
    col4.metric("🎯 Ticket Médio / Pedido", f"${avg_ticket_order:,.2f}")
    col5.metric("🪙 Ticket Médio / Item", f"${avg_ticket_item:,.2f}")

def display_products(df_summary):
    st.markdown("### 📊 Visuais de Desempenho por Produto")

    df_sorted = df_summary.groupby("PRODUCT_NAME")["TOTAL_GROSS_VALUE"].sum().nlargest(10).reset_index()
    st.plotly_chart(
        px.bar(df_sorted, x="PRODUCT_NAME", y="TOTAL_GROSS_VALUE", color="PRODUCT_NAME", title="Vendas por Produto"),
        use_container_width=True
    )

    st.plotly_chart(
        px.bar(df_summary, x="CARD_TYPE", y="TOTAL_GROSS_VALUE", color="CARD_TYPE", title="Vendas por Tipo de Cartão"),
        use_container_width=True
    )

def display_clients(df_summary):
    st.markdown("### 📊 Visuais de Desempenho por Cliente")

    st.plotly_chart(px.bar(df_summary.groupby("SALES_REASON_NAME")["TOTAL_GROSS_VALUE"].sum().reset_index(), x="SALES_REASON_NAME", y="TOTAL_GROSS_VALUE", title="📊 Valor Negociado por Motivo"), use_container_width=True)

    st.plotly_chart(
        px.bar(df_summary, x="CUSTOMER_FULL_NAME", y="TOTAL_GROSS_VALUE", title="📊 Valor Negociado por Cliente"),
        use_container_width=True
    )

# 🧠 Execução principal
st.title("📊 Sales Performance Dashboard")
st.caption("Desenvolvido com Streamlit + Snowflake")

if "df_combined" not in st.session_state:
    st.session_state.df_combined = None

if st.sidebar.button("📥 Carregar Dados"):
    st.session_state.df_combined = get_combined_data()

if st.session_state.df_combined is not None:
    df_raw = st.session_state.df_combined
    df = calculate_metrics(df_raw)
    df_filtered = display_filters(df)

    df_summary = generate_summary(df_filtered)

    tabs = st.tabs(["📈 Visão Geral", "📦 Produtos", "🧍 Clientes", "🌍 Localização"])
    with tabs[0]:
        display_kpis_general(df_filtered, df)
        display_general(df_summary, df_filtered)
    with tabs[1]:
        st.markdown("### Detalhamento Produtos")
        display_kpis_products(df_filtered)
        display_products(df_summary)
        st.dataframe(df_filtered)
    with tabs[2]:
        st.markdown("### Detalhamento clientes")
        display_clients(df_summary)
        st.dataframe(df_filtered)
    with tabs[3]:
        st.markdown("### Detalhamento localização")
        st.dataframe(df_filtered)