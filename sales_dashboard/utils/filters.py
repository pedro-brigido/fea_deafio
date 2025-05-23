
import pandas as pd
import streamlit as st

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
