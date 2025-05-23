import streamlit as st
from utils.data_loader import load_data
from utils.metrics import calculate_metrics, generate_summary
from utils.filters import display_filters
from modules.overview import display_kpis_general, display_general
from modules.products import display_products_advanced
from modules.clients import display_clients_advanced
from modules.location import display_location_analysis

# --------------------------------------------------------------------
# 🎛️ Configuração da Aplicação
# --------------------------------------------------------------------
st.set_page_config(page_title="📊 Sales Performance Dashboard", layout="wide")
st.title("📊 Sales Performance Dashboard")
st.caption("📦 Ecommerce - Adventure Works (dados fictícios)")

# --------------------------------------------------------------------
# 📥 Carga de Dados com Controle de Sessão
# --------------------------------------------------------------------
if "df_combined" not in st.session_state:
    st.session_state.df_combined = None

with st.sidebar:
    st.header("🔧 Controles")

    # Botão de carregamento inicial
    if st.button("📥 Carregar Dados"):
        with st.spinner("Carregando dados do Snowflake..."):
            st.session_state.df_combined = load_data()

    # Botão para forçar atualização (ignora cache)
    if st.button("🔄 Atualizar Dados"):
        with st.spinner("Atualizando dados..."):
            st.cache_data.clear()
            st.session_state.df_combined = load_data()

# --------------------------------------------------------------------
# 🧠 Processamento e Exibição do Dashboard
# --------------------------------------------------------------------
if st.session_state.df_combined is not None:
    df_raw = st.session_state.df_combined
    df = calculate_metrics(df_raw)
    df_filtered = display_filters(df)
    df_summary = generate_summary(df_filtered)

    # Abas principais do dashboard
    tabs = st.tabs(["📈 Visão Geral", "📦 Produtos", "🧍 Clientes", "🌍 Localização"])

    with tabs[0]:
        display_kpis_general(df_filtered, df)
        display_general(df_filtered)

    with tabs[1]:
        display_products_advanced(df_filtered)

    with tabs[2]:
        display_clients_advanced(df_filtered)

    with tabs[3]:
        display_location_analysis(df_filtered)

else:
    st.info("👈 Clique no botão '📥 Carregar Dados' na barra lateral para iniciar.")
