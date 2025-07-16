# FEA Desafio

This repository contains a dbt project used to build an analytics
warehouse on Snowflake as well as a Streamlit dashboard for
visualising sales performance.  The models are based on the
Adventure Works dataset and generate a star schema with dimensional
and fact tables.  The `sales_dashboard` folder exposes a web
application that queries the warehouse using Snowflake credentials
provided via environment variables.

## Repository structure

```
├── models/                # dbt models (staging and marts)
├── seeds/                 # seed files loaded into Snowflake
├── resources/             # architecture diagram of the warehouse
├── sales_dashboard/       # Streamlit application
├── requirements.txt       # dependencies for dbt
└── sales_dashboard/requirements.txt
```

The folder `resources` contains `fea_dw.png` with a diagram of the
warehouse design.

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

With the environment variables set, execute the following commands to
build the warehouse:

```bash
dbt seed      # load seed files
(db) dbt run  # build models
(db) dbt test # run tests defined in the project
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
