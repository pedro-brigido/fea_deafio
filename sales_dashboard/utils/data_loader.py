import pandas as pd
import streamlit as st
import os
from dotenv import load_dotenv
import snowflake.connector as sc

load_dotenv()

@st.cache_data(ttl="1h")
def load_data(schema="CEA_PBRIGIDO_MARTS", database="FEA24_11"):
    creds = {
        "account": os.getenv("DEV_SNOWFLAKE_ACCOUNT"),
        "database": database,
        "schema": "RAW_ADVENTURE_WORKS",
        "warehouse": os.getenv("DEV_SNOWFLAKE_WAREHOUSE"),
        "role": os.getenv("DEV_SNOWFLAKE_ROLE"),
        "user": os.getenv("DEV_SNOWFLAKE_USER"),
        "password": os.getenv("DEV_SNOWFLAKE_PASSWORD"),
    }

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
        with sc.connect(**creds) as conn:
            df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return None