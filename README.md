# FEAdesafio Project

This repository contains a [dbt](https://www.getdbt.com/) project and a Streamlit dashboard built to explore the Adventure Works sales dataset.

## Requirements

- Python 3.9+
- Snowflake account (for running dbt models and loading data)

Install the Python dependencies used by dbt:

```bash
pip install -r requirements.txt
```

The Streamlit dashboard has its own requirements list:

```bash
pip install -r sales_dashboard/requirements.txt
```

## Configuration

Database credentials are read from environment variables. Copy `.env.example` to `.env` and fill in your Snowflake connection details before running any commands.

## Running dbt

With the environment variables configured you can build the warehouse:

```bash
dbt run
```

Run tests defined in the models:

```bash
dbt test
```

## Launching the Dashboard

After installing the dashboard requirements you can launch the interactive sales dashboard with:

```bash
streamlit run sales_dashboard/main.py
```

The dashboard queries the Snowflake warehouse using the credentials defined in your environment.

## Repository Layout

- `models/` – dbt models organised into `staging` and `marts` layers.
- `seeds/` – seed CSV files loaded by dbt (e.g. `geolocations.csv`).
- `sales_dashboard/` – Streamlit application and helper modules.
- `resources/` – diagrams and additional assets.
- `dbt_project.yml` – dbt project configuration.
- `profiles.yml` – default dbt profile used for Snowflake connections.

## Notes

This repository does not include the Snowflake account information. Ensure the environment variables in `.env` are set correctly.

