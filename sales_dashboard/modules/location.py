import streamlit as st
import plotly.express as px
import pandas as pd
from utils.visuals import geocode_dataframe
from utils.data_loader import load_data

def display_location_analysis(df):
    st.markdown("## 🌍 Desempenho Geográfico de Vendas")
    st.caption("Compreenda onde estão seus principais mercados e oportunidades de expansão.")
    st.markdown("---")

    # KPIs
    by_city = df.groupby("CITY")["NET_TOTAL"].sum()
    by_state = df.groupby("STATE_NAME")["NET_TOTAL"].sum()
    by_country = df.groupby("COUNTRY_NAME")["NET_TOTAL"].sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("🏙️ Cidade com Maior Receita", by_city.idxmax(), f"R$ {by_city.max():,.2f}")
    col2.metric("🗽️ Estado com Maior Receita", by_state.idxmax(), f"R$ {by_state.max():,.2f}")
    col3.metric("🌐 País com Maior Receita", by_country.idxmax(), f"R$ {by_country.max():,.2f}")

    st.markdown("---")
    dim_map = {"Cidade": "CITY", "Estado": "STATE_NAME", "País": "COUNTRY_NAME"}
    dim_label = st.selectbox("Selecione a dimensão geográfica:", list(dim_map.keys()))
    dim = dim_map[dim_label]
    print(dim)

    st.subheader("🌍 Receita por Cidade no Globo")
    df_map = df.groupby([dim]).agg({
        "NET_TOTAL": "sum",
        "PK_SALES_ORDER": "nunique",
        "ORDER_QUANTITY": "sum"
    }).reset_index().rename(columns={
        "PK_SALES_ORDER": "Total Pedidos",
        "ORDER_QUANTITY": "Qtd Vendida",
        "NET_TOTAL": "Receita"
    })

    # Reading geolocation
    df_geo = load_data("SELECT * FROM FEA24_11.CEA_PBRIGIDO_SEEDS.GEOLOCATIONS")
    df_map_geo = df_map.merge(df_geo.drop_duplicates(subset=[dim]), how="inner", on=[dim])

    # Plot map
    fig_map = px.scatter_geo(
        df_map_geo,
        lat="LATITUDE", 
        lon="LONGITUDE",
        color="Receita",
        size="Receita",
        hover_name=dim,
        projection="natural earth",
        color_continuous_scale="Viridis",
        title="🌍 Receita Global por Cidade",
        size_max=40
    )
    fig_map.update_traces(marker=dict(line=dict(width=0.8, color="white"), sizemode='area'))
    fig_map.update_layout(geo=dict(showland=True), height=600, margin=dict(l=0, r=0, t=50, b=20))
    st.plotly_chart(fig_map, use_container_width=True)

    st.subheader("💡 Produtos com Maior Ticket Médio por Região")
    dim_map = {"Cidade": "CITY", "Estado": "STATE_NAME", "País": "COUNTRY_NAME"}
    dim_label = st.selectbox("Selecione a dimensão geográfica:", list(dim_map.keys()), key="box_2")
    dim = dim_map[dim_label]

    ticket_df = df.groupby([dim, "PRODUCT_NAME"]).agg({
        "NET_TOTAL": "sum",
        "PK_SALES_ORDER": "nunique"
    }).reset_index()
    ticket_df["Ticket Médio"] = ticket_df["NET_TOTAL"] / ticket_df["PK_SALES_ORDER"]

    top_tickets = ticket_df.sort_values("Ticket Médio", ascending=False).head(20)
    fig_ticket = px.bar(
        top_tickets.sort_values("Ticket Médio", ascending=True),
        x="Ticket Médio", y="PRODUCT_NAME", color=dim,
        orientation="h",
        title=f"Top 20 Ticket Médio por Produto e {dim_label}"
    )
    fig_ticket.update_traces(texttemplate='R$ %{x:,.2f}', textposition="outside")
    fig_ticket.update_layout(height=max(500, len(top_tickets)*30))
    st.plotly_chart(fig_ticket, use_container_width=True)

    st.markdown("---")

    df_map = df.groupby(["CITY", "STATE_NAME", "COUNTRY_NAME"]).agg({
        "NET_TOTAL": "sum",
        "PK_SALES_ORDER": "nunique",
        "ORDER_QUANTITY": "sum"
    }).reset_index().rename(columns={
        "PK_SALES_ORDER": "Total Pedidos",
        "ORDER_QUANTITY": "Qtd Vendida",
        "NET_TOTAL": "Receita"
    })
    st.subheader("📍 Detalhamento por Localidade")
    top_locs = df_map.sort_values("Receita", ascending=False).head(10).copy()
    top_locs.insert(0, "Ranking", range(1, len(top_locs)+1))
    st.dataframe(top_locs[["Ranking", "CITY", "STATE_NAME", "COUNTRY_NAME", "Receita", "Total Pedidos", "Qtd Vendida"]], use_container_width=True)

    st.download_button("⬇️ Baixar Dados Regionais", df_map.to_csv(index=False).encode("utf-8"), file_name="desempenho_regional.csv", mime="text/csv")
