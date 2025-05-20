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
    # st.markdown("### 📊 Indicadores por Produto")
    best_product_by_revenue = df_filtered.groupby("PRODUCT_NAME")["GROSS_TOTAL"].sum().nlargest(1).index[0]
    # best_product_by_quantity = df_filtered.groupby("PRODUCT_NAME")["ORDER_QUANTITY"].sum().nlargest(1).index[0]
    # total_orders = df_filtered["PK_SALES_ORDER"].nunique()
    # total_qty = df_filtered["ORDER_QUANTITY"].sum()
    # avg_ticket_order = df_filtered["GROSS_TOTAL"].sum() / df_filtered["PK_SALES_ORDER"].nunique()
    # avg_ticket_item = df_filtered["GROSS_TOTAL"].sum() / df_filtered["ORDER_QUANTITY"].sum()
    # greater_average_ticket = df_filtered.groupby("PRODUCT_NAME")["GROSS_TOTAL"].sum().nlargest(1).index[0]

    # col1, col2, col3, col4, col5 = st.columns(5)
    
    # col1.metric("🎯 Melhor produto em receita", best_product_by_revenue)
    # col2.metric("🪙 Melhor produto em quantidade vendida", best_product_by_quantity)
    # col3.metric("📦 Total pedidos/total produtos vendidos", f"{total_orders}/{total_qty}")
    # col4.metric("🎯 Ticket Médio / Pedido", f"${avg_ticket_order:,.2f}")
    # col5.metric("🪙 Ticket Médio / Item", f"${avg_ticket_item:,.2f}")

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

# 🆕 Página de Produtos Avançada
def display_products_advanced(df):
    st.markdown("## 🧾 Visão Analítica de Produtos")

    # KPI
    total_orders = df_filtered["PK_SALES_ORDER"].nunique()
    total_qty = df_filtered["ORDER_QUANTITY"].sum()
    product_revenue = df.groupby("PRODUCT_NAME")["GROSS_TOTAL"].sum()
    product_qty = df.groupby("PRODUCT_NAME")["ORDER_QUANTITY"].sum()
    product_ticket = df.groupby("PRODUCT_NAME").apply(lambda x: (x["GROSS_TOTAL"].sum() - (x["GROSS_TOTAL"] * x["UNIT_PRICE_DISCOUNT"]).sum()) / x["PK_SALES_ORDER"].nunique()).sort_values(ascending=False)
    avg_ticket_item = df_filtered["GROSS_TOTAL"].sum() / df_filtered["ORDER_QUANTITY"].sum()

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("💰 Produto com Maior Receita", product_revenue.idxmax(), f"${product_revenue.max():,.2f}")
    col2.metric("📦 Produto Mais Vendido (Qtd)", product_qty.idxmax(), int(product_qty.max()))
    col3.metric("🎯 Maior Ticket Médio", product_ticket.index[0], f"${product_ticket.iloc[0]:,.2f}")
    col4.metric("📦 Total pedidos/total produtos vendidos", f"{total_orders}/{total_qty}")
    col5.metric("🪙 Ticket Médio / Item", f"${avg_ticket_item:,.2f}")

    # Tabela detalhada com ordenação
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

    st.markdown("### 📋 Ranking de Produtos")

    df_sorted = product_table.groupby("PRODUCT_NAME")["Valor Bruto"].sum().nlargest(10).reset_index()
    st.plotly_chart(
        px.bar(df_sorted, x="PRODUCT_NAME", y="Valor Bruto", color="PRODUCT_NAME", title="Vendas por Produto"),
        use_container_width=True
    )

    # Análise Promoção
    promo_df = df[df["SALES_REASON_NAME"] == "On Promotion"]
    top_promo = promo_df.groupby("PRODUCT_NAME")["ORDER_QUANTITY"].sum().nlargest(5).reset_index()
    if not top_promo.empty:
        st.markdown(f"### 🎁 Produto com mais vendas em 'Promotion': `{top_promo.iloc[0, 0]}` ({top_promo.iloc[0, 1]} unidades)")
        st.plotly_chart(px.bar(top_promo, x="PRODUCT_NAME", y="ORDER_QUANTITY", title="Top Produtos em Promoções"), use_container_width=True)

    # Análise por Geografia
    st.markdown("### 🌍 Ticket Médio por Produto e Localização")
    dim = st.selectbox("Selecionar dimensão:", ["CITY", "STATE_NAME", "COUNTRY_NAME"])
    geo_group = df.groupby(["PRODUCT_NAME", dim])["NET_TOTAL"].sum() / df.groupby(["PRODUCT_NAME", dim])["PK_SALES_ORDER"].nunique()
    geo_df = geo_group.reset_index(name="Ticket Médio")
    st.plotly_chart(px.bar(geo_df.sort_values("Ticket Médio", ascending=False).head(20), x="PRODUCT_NAME", y="Ticket Médio", color=dim, title="Ticket Médio por Produto e Localidade"), use_container_width=True)

    # Gráficos adicionais
    st.markdown("### 📊 Distribuição por Tipo de Cartão e Motivo")
    # col1, col2 = st.columns(2)
    card_fig = px.bar(df.groupby(["PRODUCT_NAME", "CARD_TYPE"])["ORDER_QUANTITY"].sum().reset_index(), x="PRODUCT_NAME", y="ORDER_QUANTITY", color="CARD_TYPE", title="Vendas por Produto e Cartão")
    reason_fig = px.bar(df.groupby(["PRODUCT_NAME", "SALES_REASON_NAME"])["ORDER_QUANTITY"].sum().reset_index(), x="PRODUCT_NAME", y="ORDER_QUANTITY", color="SALES_REASON_NAME", title="Vendas por Produto e Motivo")
    st.plotly_chart(card_fig, use_container_width=True)
    st.plotly_chart(reason_fig, use_container_width=True)

def display_clients(df_summary):
    st.markdown("### 📊 Visuais de Desempenho por Cliente")

    st.plotly_chart(px.bar(df_summary.groupby("SALES_REASON_NAME")["TOTAL_GROSS_VALUE"].sum().reset_index(), x="SALES_REASON_NAME", y="TOTAL_GROSS_VALUE", title="📊 Valor Negociado por Motivo"), use_container_width=True)

    st.plotly_chart(
        px.bar(df_summary, x="CUSTOMER_FULL_NAME", y="TOTAL_GROSS_VALUE", title="📊 Valor Negociado por Cliente"),
        use_container_width=True
    )

def display_clients_advanced(df):
    st.markdown("## 🧍 Visão Analítica de Clientes")
    df_clients = df.copy()
    # # Filtros
    # with st.expander("🎛️ Filtros de Cliente"):
    #     products = st.multiselect("Produto", df["PRODUCT_NAME"].unique())
    #     cards = st.multiselect("Tipo de Cartão", df["CARD_TYPE"].unique())
    #     reasons = st.multiselect("Motivo de Venda", df["SALES_REASON_NAME"].unique())
    #     status = st.multiselect("Status do Pedido", df["STATUS"].unique())

    # df_clients = df.copy()
    # if products:
    #     df_clients = df_clients[df_clients["PRODUCT_NAME"].isin(products)]
    # if cards:
    #     df_clients = df_clients[df_clients["CARD_TYPE"].isin(cards)]
    # if reasons:
    #     df_clients = df_clients[df_clients["SALES_REASON_NAME"].isin(reasons)]
    # if status:
    #     df_clients = df_clients[df_clients["STATUS"].isin(status)]

    # KPIs
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

    # Tabela top 10
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

    st.markdown("### 🧾 Top 10 Clientes")
    st.dataframe(df_top, use_container_width=True)

    # Análise de comportamento
    selected_client = st.selectbox("📍 Selecione um cliente para análise", df_top["CUSTOMER_FULL_NAME"])
    df_sel = df_clients[df_clients["CUSTOMER_FULL_NAME"] == selected_client]

    col1, col2 = st.columns(2)
    prod_fig = px.bar(df_sel.groupby("PRODUCT_NAME")["ORDER_QUANTITY"].sum().reset_index(), x="PRODUCT_NAME", y="ORDER_QUANTITY", title="Produtos Mais Comprados")
    card_fig = px.pie(df_sel, names="CARD_TYPE", title="Preferência de Cartão", values="NET_TOTAL")
    col1.plotly_chart(prod_fig, use_container_width=True)
    col2.plotly_chart(card_fig, use_container_width=True)

    st.plotly_chart(px.bar(df_sel.groupby("SALES_REASON_NAME")["NET_TOTAL"].sum().reset_index(), x="SALES_REASON_NAME", y="NET_TOTAL", title="Motivos de Venda Mais Comuns"), use_container_width=True)

    # Informações gerais
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

def display_location_analysis(df):
    st.markdown("## 🌍 Visão Geográfica de Vendas")

    # KPIs
    revenue_by_city = df.groupby("CITY")["NET_TOTAL"].sum()
    revenue_by_state = df.groupby("STATE_NAME")["NET_TOTAL"].sum()
    revenue_by_country = df.groupby("COUNTRY_NAME")["NET_TOTAL"].sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("🏙️ Cidade com Maior Receita", revenue_by_city.idxmax(), f"${revenue_by_city.max():,.2f}")
    col2.metric("🗺️ Estado com Maior Receita", revenue_by_state.idxmax(), f"${revenue_by_state.max():,.2f}")
    col3.metric("🌐 País com Maior Receita", revenue_by_country.idxmax(), f"${revenue_by_country.max():,.2f}")

    # Mapa Interativo
    st.markdown("### 🗺️ Mapa de Vendas por Cidade")
    df_map = df.groupby(["CITY", "STATE_NAME", "COUNTRY_NAME"]).agg({
        "NET_TOTAL": "sum",
        "PK_SALES_ORDER": "nunique",
        "ORDER_QUANTITY": "sum"
    }).reset_index().rename(columns={
        "PK_SALES_ORDER": "Total Pedidos",
        "ORDER_QUANTITY": "Qtd Vendida",
        "NET_TOTAL": "Receita"
    })
    df_map["Local"] = df_map["CITY"] + ", " + df_map["STATE_NAME"] + ", " + df_map["COUNTRY_NAME"]
    map_fig = px.scatter_geo(df_map, locationmode="country names", 
                             locations="COUNTRY_NAME", color="Receita", 
                             hover_name="Local", size="Receita", 
                             title="Receita por Localidade (País/Cidade)",
                             custom_data=["CITY", "STATE_NAME", "COUNTRY_NAME"])
    map_fig.update_traces(marker=dict(line=dict(width=0.5, color='DarkSlateGrey')),
                          selector=dict(mode='markers'))
    selected_location = st.plotly_chart(map_fig, use_container_width=True)

    clicked_location = st.session_state.get("clicked_location")

    if clicked_location:
        city, state, country = clicked_location
        st.info(f"🔍 Filtro aplicado: {city}, {state}, {country}")
        df = df[(df["CITY"] == city) & (df["STATE_NAME"] == state) & (df["COUNTRY_NAME"] == country)]

    # Tabela Top 5 Cidades
    st.markdown("### 🧾 Top 5 Cidades por Receita")
    top_cities = df_map.sort_values("Receita", ascending=False).head(5).copy()
    top_cities.insert(0, "Ranking", range(1, 6))
    st.dataframe(top_cities[["Ranking", "CITY", "STATE_NAME", "COUNTRY_NAME", "Receita", "Total Pedidos", "Qtd Vendida"]], use_container_width=True)

    # # Filtros adicionais
    # with st.expander("🎛️ Filtros de Localização"):
    #     product = st.multiselect("Produto", df["PRODUCT_NAME"].dropna().unique())
    #     card = st.multiselect("Cartão", df["CARD_TYPE"].dropna().unique())
    #     reason = st.multiselect("Motivo", df["SALES_REASON_NAME"].dropna().unique())
    #     status = st.multiselect("Status", df["STATUS"].dropna().unique())
    #     client = st.multiselect("Cliente", df["CUSTOMER_FULL_NAME"].dropna().unique())

    # df_loc = df.copy()
    # if product:
    #     df_loc = df_loc[df_loc["PRODUCT_NAME"].isin(product)]
    # if card:
    #     df_loc = df_loc[df_loc["CARD_TYPE"].isin(card)]
    # if reason:
    #     df_loc = df_loc[df_loc["SALES_REASON_NAME"].isin(reason)]
    # if status:
    #     df_loc = df_loc[df_loc["STATUS"].isin(status)]
    # if client:
    #     df_loc = df_loc[df_loc["CUSTOMER_FULL_NAME"].isin(client)]
    df_loc = df.copy()
    st.markdown("### 📍 Desempenho Regional Detalhado")
    location_perf = df_loc.groupby(["CITY", "STATE_NAME", "COUNTRY_NAME"]).agg({
        "PK_SALES_ORDER": "nunique",
        "ORDER_QUANTITY": "sum",
        "NET_TOTAL": "sum"
    }).reset_index().rename(columns={
        "PK_SALES_ORDER": "Pedidos",
        "ORDER_QUANTITY": "Qtd Comprada",
        "NET_TOTAL": "Total Receita"
    })
    st.dataframe(location_perf.sort_values("Total Receita", ascending=False), use_container_width=True)

    # Produtos com maior ticket por local
    st.markdown("### 🧮 Produtos com Maior Ticket Médio por Local")
    geo = st.selectbox("Selecione a dimensão geográfica:", ["CITY", "STATE_NAME", "COUNTRY_NAME"])
    ticket_geo = df.groupby([geo, "PRODUCT_NAME"])["NET_TOTAL"].sum() / df.groupby([geo, "PRODUCT_NAME"])["PK_SALES_ORDER"].nunique()
    ticket_geo = ticket_geo.reset_index(name="Ticket Médio")
    st.plotly_chart(px.bar(ticket_geo.sort_values("Ticket Médio", ascending=False).head(20), x="PRODUCT_NAME", y="Ticket Médio", color=geo, title="Ticket Médio por Produto e Região"), use_container_width=True)


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
        display_products_advanced(df_filtered)
    with tabs[2]:
        st.markdown("### Detalhamento clientes")
        display_clients_advanced(df_filtered)
    with tabs[3]:
        st.markdown("### Detalhamento localização")
        display_location_analysis(df_filtered)