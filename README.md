# FEA Desafio

This repository contains a dbt project used to build an analytics
warehouse on Snowflake as well as a Streamlit dashboard for
visualising sales performance.  The models are based on the
Adventure Works dataset and generate a star schema with dimensional
and fact tables.  The `sales_dashboard` folder exposes a web
application that queries the warehouse using Snowflake credentials
provided via environment variables.

## Overview/Context

Adventure Works (AW) is a fast‑growing bicycle manufacturer with 500+ products, 20 000 customers and 31 000 orders. To sustain this trajectory and beat the competition, AW’s leadership has launched a programme to become data‑driven by building a modern analytics platform.

The initial milestone focuses on the Sales domain, but datasets from the ERP (SAP), CRM (Salesforce), Web Analytics (Google Analytics) and the Wordpress web store will soon follow. The initiative is championed by Innovation Director João Muller and backed by CEO Carlos Silveira, who demands iron‑clad data quality — for instance, 2011 gross sales must reconcile to US$ 12 646 112.16 as audited.

Commercial Director Silvana Teixeira questions the ROI versus promotional spend, while IT Director Nilson Ramos must deliver with limited DBA bandwidth. The project therefore prioritises quick wins, automated quality tests and clear stakeholder communication to prove value early and often. Take a look at the dimensional model built on top of ADW dataset bellow:

![Dimensional model for Adventure Works](resources/fea_dw.png)

## Repository structure

```
├── models/                # dbt models (staging and marts)
├── seeds/                 # seed files loaded into Snowflake
├── resources/             # architecture diagram of the warehouse
├── sales_dashboard/       # Streamlit application
├── requirements.txt       # dependencies for dbt
└── sales_dashboard/requirements.txt # dependencies for dash
```

## Requirements

- Python 3.10+
- Snowflake account with appropriate permissions
- [dbt-snowflake](https://docs.getdbt.com/reference/warehouse-setups/snowflake-profile) `1.8.3`
- Additional packages listed in `sales_dashboard/requirements.txt`

## Setup

1. Clone this repository and create a virtual environment.
2. Install the dbt dependencies:

```bash
pip install -r requirements.txt
```

3. Install the dashboard requirements:

```bash
pip install -r sales_dashboard/requirements.txt
```

4. Copy `.env.example` to `.env` and fill in your Snowflake
   credentials or configure them directly as environment variables.
5. Ensure the profile in `profiles.yml` matches your Snowflake
   connection information.

## Running dbt

With the environment variables set, execute the following command to
build the warehouse:

```bash
dbt build # test and build all models
```

The generated schemas will be created under the database and schema
configured in your profile.

## Running the dashboard

After building the models you can launch the Streamlit dashboard:

```bash
streamlit run sales_dashboard/main.py
```

The application queries the Snowflake warehouse using the same
credentials defined in your `.env` file or Streamlit `secrets.toml`.

## License

This project is provided for educational purposes.  See the source for
full details.
