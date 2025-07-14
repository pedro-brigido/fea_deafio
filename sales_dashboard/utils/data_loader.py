import pandas as pd
import streamlit as st
import os
from dotenv import load_dotenv
import snowflake.connector as sc

load_dotenv()

@st.cache_data(ttl=3600)
def load_data(query, schema="CEA_PBRIGIDO_MARTS", database="FEA24_11"):
    creds = {
        "account": os.getenv("DEV_SNOWFLAKE_ACCOUNT"),
        "database": database,
        "schema": schema,
        "warehouse": os.getenv("DEV_SNOWFLAKE_WAREHOUSE"),
        "role": os.getenv("DEV_SNOWFLAKE_ROLE"),
        "user": os.getenv("DEV_SNOWFLAKE_USER"),
        "password": os.getenv("DEV_SNOWFLAKE_PASSWORD"),
    }

    try:
        with sc.connect(**creds) as conn:
            df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return None