import streamlit as st
from datetime import datetime
from utils.data_loader import load_data
from sales_dashboard.utils.df_cleaning import dedup_and_cast_df
from utils.filters import display_filters, apply_filters
from modules.overview import display_kpis_general, display_general
from modules.products import display_products_advanced
from modules.clients import display_clients_advanced
from modules.location import display_location_analysis

QUERY = f"""
    SELECT
        fso.*,
        dp.PRODUCT_NAME,
        dcc.CARD_TYPE,
        dsr.SALES_REASON_NAME,
        dc.CUSTOMER_FULL_NAME,
        da.CITY, 
        da.STATE_NAME, 
        da.COUNTRY_NAME,
        dd.ORDER_YEAR,
        dd.YEAR_MONTH
    FROM FEA24_11.CEA_PBRIGIDO_MARTS.FCT_SALES_ORDERS fso
    LEFT JOIN FEA24_11.CEA_PBRIGIDO_MARTS.DIM_PRODUCTS dp ON fso.FK_PRODUCT = dp.PK_PRODUCT
    LEFT JOIN FEA24_11.CEA_PBRIGIDO_MARTS.DIM_CREDIT_CARDS dcc ON fso.FK_CREDIT_CARD = dcc.PK_CREDIT_CARD
    LEFT JOIN FEA24_11.CEA_PBRIGIDO_MARTS.DIM_SALES_REASONS dsr ON fso.PK_SALES_ORDER = dsr.PK_SALES_ORDER
    LEFT JOIN FEA24_11.CEA_PBRIGIDO_MARTS.DIM_CUSTOMERS dc ON fso.FK_CUSTOMER = dc.PK_CUSTOMER
    LEFT JOIN FEA24_11.CEA_PBRIGIDO_MARTS.DIM_ADDRESSES da ON fso.FK_SHIP_TO_ADDRESS = da.PK_ADDRESS
    LEFT JOIN FEA24_11.CEA_PBRIGIDO_MARTS.DIM_DATES dd ON fso.ORDER_DATE = dd.ORDER_DATE;
    """

st.set_page_config(layout="wide")
st.title("📦 Adventure Works")
st.caption("Performance de Vendas")

if "df_combined" not in st.session_state:
    st.session_state.df_combined = None

with st.sidebar:

    st.header("🔧 Controles")

    # Botão para forçar atualização (ignora cache)
    if st.button("🔄 Atualizar Dados"):
        with st.spinner("Atualizando dados..."):
            st.cache_data.clear()
            st.session_state.df_combined = load_data(QUERY)

# Carregamento inicial dos dados
st.session_state.df_combined = load_data(QUERY)

if st.session_state.df_combined is not None:
    st.sidebar.success(f"Dados carregados: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    df_raw = st.session_state.df_combined
    df = dedup_and_cast_df(df_raw)
    (date_range, product_filter, card_type_filter, city_filter, state_filter, 
     country_filter, reason_filter, status_filter) = display_filters(df)
    df_filtered = apply_filters(df, date_range, product_filter, card_type_filter, city_filter, 
                                state_filter, country_filter, reason_filter, status_filter)
    df_raw_filtered = apply_filters(df_raw, date_range, product_filter, card_type_filter, city_filter, 
                                    state_filter, country_filter, reason_filter, status_filter)

    # Abas principais do dashboard
    tabs = st.tabs(["📈 Visão Geral", "📦 Produtos", "🧍 Clientes", "🌍 Localização"])

    with tabs[0]:
        display_kpis_general(df_filtered, df)
        display_general(df_filtered)

    with tabs[1]:
        display_products_advanced(df_filtered, df_raw_filtered)

    with tabs[2]:
        display_clients_advanced(df_filtered, df_raw_filtered)

    with tabs[3]:
        display_location_analysis(df_filtered)

else:
    st.info("👈 Clique no botão '📥 Carregar Dados' na barra lateral para iniciar.")
