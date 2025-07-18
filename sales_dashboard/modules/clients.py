import streamlit as st
import plotly.express as px
import pandas as pd
from utils.data_loader import *

def display_clients_advanced(df_filtered: pd.DataFrame, df: pd.DataFrame):
    st.markdown("## 🧍 Detalhamento Clientes")
    st.markdown("---")

    df_clients = df.copy()

    client_total = df_filtered.groupby("CUSTOMER_FULL_NAME")["GROSS_TOTAL"].sum()
    top_10 = client_total.nlargest(10)
    top_1_name = top_10.idxmax()
    top_1_value = top_10.max()
    top_10_pct = top_10.sum() / df_filtered["GROSS_TOTAL"].sum() * 100
    freq = df_filtered["PK_SALES_ORDER"].nunique() / df_filtered["CUSTOMER_FULL_NAME"].nunique()
    top_10_no_reset = top_10
    top_10 = top_10.reset_index()

    col1, col2 = st.columns([4, 2])
    with col1:
        st.subheader("🏅 Top 10 Clientes por Receita Bruta")
        fig_top_clients = px.bar(
            top_10.sort_values("GROSS_TOTAL", ascending=True),
            x="GROSS_TOTAL", y="CUSTOMER_FULL_NAME", orientation="h",
            labels={"CUSTOMER_FULL_NAME": "Cliente", "GROSS_TOTAL": "Receita ($)"},
            text="GROSS_TOTAL",
        )
        fig_top_clients.update_traces(texttemplate='$ %{text:,.2f}', 
                                      textposition='inside', textfont=dict(color="black", family="Arial Black", size=13)
        )
        st.plotly_chart(fig_top_clients, use_container_width=True)

    with col2:
        st.metric("🏆 Cliente com Maior Receita", top_1_name, f"$ {top_1_value:,.2f}")
        st.metric("💼 % Receita dos Top 10", f"{top_10_pct:.2f}%")
        st.metric("📅 Freq. Média de Compra", f"{freq:.2f} pedidos/cliente")
        st.metric("📈 Receita Total (Top 10)", f"$ {top_10['GROSS_TOTAL'].sum():,.2f}")
        st.metric("👥 Total de Clientes", len(df_filtered["CUSTOMER_FULL_NAME"].unique()))

    st.markdown("---")

    st.subheader("🎯 Fatores que Influenciaram Compras")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Distribuição por Tipo de Cartão")
        fig_card = px.bar(df_filtered.fillna({"CARD_TYPE": "Outro"}).groupby("CARD_TYPE").size().sort_values(ascending=False).reset_index(name="count"), x="CARD_TYPE", 
                          y="count",
                          labels={"CARD_TYPE": "Tipo de Cartão", "count": "Quantidade de Pedidos"},
                          text="count")
        fig_card.update_traces(textposition="outside", textfont=dict(color="white", family="Arial Black", size=10))
        st.plotly_chart(fig_card, use_container_width=True)

    with col2:
        st.markdown("### Distribuição por motivo de compra")
        reason_counts = (
            df_clients.dropna(subset=["SALES_REASON_NAME"])
            .groupby("SALES_REASON_NAME")
            .size()
            .reset_index(name="Ocorrências")
            .sort_values("Ocorrências", ascending=False)
        )
        fig_reasons = px.bar(
            reason_counts, x="SALES_REASON_NAME", y="Ocorrências",
            labels={"SALES_REASON_NAME": "Motivo"}, text="Ocorrências",
        )
        fig_reasons.update_traces(textposition="outside", textfont=dict(color="white", family="Arial Black", size=10))
        st.plotly_chart(fig_reasons, use_container_width=True)

    st.markdown("---")

    client_summary = df_clients.groupby("CUSTOMER_FULL_NAME").agg(
        Receita=("GROSS_TOTAL", "sum"),
        Pedidos=("PK_SALES_ORDER", "nunique"),
        Quantidade_Comprada=("ORDER_QUANTITY", "sum"),
        Ultima_Compra=("ORDER_DATE", "max")
    )
    client_summary["Ticket Médio"] = client_summary["Receita"] / client_summary["Pedidos"]
    
    st.subheader("Distribuição de Clientes: Receita x Frequência e Ticket Médio")
    bubble_data = client_summary.reset_index()
    fig_bubble = px.scatter(
        bubble_data,
        x="Pedidos", y="Receita",
        size="Quantidade_Comprada", color="Ticket Médio",
        hover_name="CUSTOMER_FULL_NAME",
        labels={"Pedidos": "Nº de Pedidos", "Receita": "Receita ($)", "Quantidade_Comprada": "Qtd Comprada", "Ticket Médio": "Ticket Médio ($)"},
        # title="Distribuição de Receita vs. Frequência de Compra"
    )
    fig_bubble.update_layout(
        height=600,
        xaxis=dict(title="Frequência de Compras (Pedidos)", gridcolor="lightgrey"),
        yaxis=dict(title="Receita Total ($)", gridcolor="lightgrey"),
        legend_title="Ticket Médio ($)",
        margin=dict(l=40, r=40, t=60, b=40),
        plot_bgcolor="#222222"
    )
    fig_bubble.update_traces(
        marker=dict(opacity=0.6, line=dict(width=2, color="#027392"), sizeref=3.5, sizemode="area")
    )
    st.plotly_chart(fig_bubble, use_container_width=True)

    st.subheader("Ranking dos Top 10 Clientes")
    recent = df_filtered.groupby("CUSTOMER_FULL_NAME")["ORDER_DATE"].max()
    count = df_filtered.groupby("CUSTOMER_FULL_NAME")["PK_SALES_ORDER"].nunique()
    ticket = client_total / count

    df_top = pd.DataFrame({
        "Valor Total Negociado": client_total,
        "Nº de Pedidos": count,
        "Ticket Médio": ticket,
        "Última Compra": recent
    }).loc[top_10_no_reset.index].sort_values(by="Valor Total Negociado", ascending=False)
    df_top.reset_index(inplace=True)
    df_top.index += 1
    df_top.insert(0, "Ranking", df_top.index)
    df_top.rename(columns={"CUSTOMER_FULL_NAME": "Cliente"}, inplace=True)

    st.dataframe(df_top, use_container_width=True)
