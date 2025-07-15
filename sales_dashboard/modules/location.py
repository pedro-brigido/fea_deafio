import streamlit as st
import plotly.express as px
import pandas as pd
from utils.data_loader import load_data

def display_location_analysis(df):
    st.markdown("## 🌍 Desempenho Geográfico de Vendas")
    st.caption("Compreenda onde estão seus principais mercados e oportunidades de expansão.")
    st.markdown("---")

    # KPIs
    by_city = df.groupby("CITY")["NET_TOTAL"].sum()
    by_state = df.groupby("STATE_NAME")["NET_TOTAL"].sum()
    by_country = df.groupby("COUNTRY_NAME")["NET_TOTAL"].sum()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🏙️ Cidade com Maior Receita", by_city.idxmax(), f"$ {by_city.max():,.2f}")
    col2.metric("🗽️ Estado com Maior Receita", by_state.idxmax(), f"$ {by_state.max():,.2f}")
    col3.metric("🌐 País com Maior Receita", by_country.idxmax(), f"$ {by_country.max():,.2f}")
    col4.metric("% Top 10 cidades vs Total", f"{by_city.nlargest(10).sum() / by_city.sum():.1%}", "Top 10 Receita % do total")

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
        color_continuous_scale="Cividis_r",
        title="🌍 Receita Global por Cidade",
        size_max=35,
        opacity=0.4
    )

    fig_map.update_traces(
        marker=dict(line=dict(width=0.8, color="#0d1117"), sizemode="area")
    )

    fig_map.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0d1117",
        plot_bgcolor="#0d1117",
        geo=dict(
            bgcolor="#0d1117",
            landcolor="#1a1f2b",
            showland=True,
            showcountries=True,
            countrycolor="#444",
            coastlinecolor="#444",
        ),
        height=600,
        margin=dict(l=0, r=0, t=60, b=20)
    )

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
    top_tickets.rename(columns={"PRODUCT_NAME": "Produto"}, inplace=True)
    fig_ticket = px.bar(
        top_tickets.sort_values("Ticket Médio", ascending=True),
        x="Ticket Médio", y="Produto", color=dim,
        orientation="h",
        title=f"Top 20 Ticket Médio por Produto e {dim_label}"
    )
    fig_ticket.update_traces(texttemplate='$ %{x:,.2f}', textposition="outside")
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
        "NET_TOTAL": "Receita ($)"
    })
    st.subheader("📍 Top 10 cidades por receita")
    top_locs = df_map.sort_values("Receita ($)", ascending=False).head(10).copy()
    top_locs.insert(0, "Ranking", range(1, len(top_locs)+1))
    top_locs.rename(columns={"CITY": "Cidade", "STATE_NAME": "Estado", "COUNTRY_NAME": "País"}, inplace=True)
    st.dataframe(top_locs[["Ranking", "Cidade", "Estado", "País", "Receita ($)", "Total Pedidos", "Qtd Vendida"]], use_container_width=True)
