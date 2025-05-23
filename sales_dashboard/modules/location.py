import streamlit as st
import plotly.express as px
import pandas as pd
from utils.visuals import *
from utils.data_loader import *

def display_location_analysis(df):
    st.markdown("## 🌍 Análise Geográfica de Vendas")
    st.caption("Visualize a distribuição de receita e volume por cidades, estados e países, e descubra onde estão os maiores mercados.")

    # --- KPIs ---
    revenue_by_city = df.groupby("CITY")["NET_TOTAL"].sum()
    revenue_by_state = df.groupby("STATE_NAME")["NET_TOTAL"].sum()
    revenue_by_country = df.groupby("COUNTRY_NAME")["NET_TOTAL"].sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("🏙️ Cidade com Maior Receita", revenue_by_city.idxmax(), f"${revenue_by_city.max():,.2f}")
    col2.metric("🗺️ Estado com Maior Receita", revenue_by_state.idxmax(), f"${revenue_by_state.max():,.2f}")
    col3.metric("🌐 País com Maior Receita", revenue_by_country.idxmax(), f"${revenue_by_country.max():,.2f}")

    # --- Mapa Interativo por País ---
    st.markdown("### 🗺️ Receita por País")
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
                             title="Receita por Localidade",
                             custom_data=["CITY", "STATE_NAME", "COUNTRY_NAME"])
    map_fig.update_traces(marker=dict(line=dict(width=0.5, color='DarkSlateGrey')))
    st.plotly_chart(map_fig, use_container_width=True)

    # --- Mapa Coroplético por Estado (EUA) ---
    st.markdown("### 🗺️ Receita por Estado (EUA)")
    df_state_map = df[df["COUNTRY_NAME"] == "United States"].groupby("STATE_NAME")["NET_TOTAL"].sum().reset_index()
    fig_choro = px.choropleth(df_state_map, locations="STATE_NAME", locationmode="USA-states", color="NET_TOTAL",
                               color_continuous_scale="Blues", scope="usa", title="Receita por Estado (EUA)")
    st.plotly_chart(fig_choro, use_container_width=True)

    # --- Tabela Top 5 Cidades ---
    st.markdown("### 🧾 Top 5 Cidades por Receita")
    top_cities = df_map.sort_values("Receita", ascending=False).head(5).copy()
    top_cities.insert(0, "Ranking", range(1, 6))
    st.dataframe(top_cities[["Ranking", "CITY", "STATE_NAME", "COUNTRY_NAME", "Receita", "Total Pedidos", "Qtd Vendida"]], use_container_width=True)

    # --- Desempenho Regional Detalhado ---
    st.markdown("### 📍 Desempenho Regional Detalhado")
    location_perf = df.groupby(["CITY", "STATE_NAME", "COUNTRY_NAME"]).agg({
        "PK_SALES_ORDER": "nunique",
        "ORDER_QUANTITY": "sum",
        "NET_TOTAL": "sum"
    }).reset_index().rename(columns={
        "PK_SALES_ORDER": "Pedidos",
        "ORDER_QUANTITY": "Qtd Comprada",
        "NET_TOTAL": "Total Receita"
    })
    st.dataframe(location_perf.sort_values("Total Receita", ascending=False), use_container_width=True)

    # --- Produtos com Maior Ticket Médio por Local ---
    st.markdown("### 🧮 Produtos com Maior Ticket Médio por Local")
    geo = st.selectbox("Selecione a dimensão geográfica:", ["CITY", "STATE_NAME", "COUNTRY_NAME"])
    ticket_geo = df.groupby([geo, "PRODUCT_NAME"])["NET_TOTAL"].sum() / df.groupby([geo, "PRODUCT_NAME"])["PK_SALES_ORDER"].nunique()
    ticket_geo = ticket_geo.reset_index(name="Ticket Médio")
    st.plotly_chart(px.bar(ticket_geo.sort_values("Ticket Médio", ascending=False).head(20),
                           x="PRODUCT_NAME", y="Ticket Médio", color=geo,
                           title="Ticket Médio por Produto e Região"), use_container_width=True)
