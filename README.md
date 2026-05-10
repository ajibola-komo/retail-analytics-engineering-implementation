# Elecmart Retail Analytics Pipeline

An end-to-end data engineering project simulating a mid-sized electronics retailer's 3-year performance and covering the full analytics lifecycle: synthetic data generation, cloud storage, warehouse ingestion, dbt transformation, and Tableau dashboards.

---

## Tech Stack

| Layer | Tool |
|---|---|
| Data generation | Python (Faker, NumPy) |
| Compute & Orchestration | WS EC2 (Linux), Git-based deployment |
| Storage | Amazon S3 |
| Warehouse | Snowflake / DuckDB |
| Transformation | dbt |
| Visualization | Tableau |

---

## Architecture

The pipeline follows a Medallion Architecture implemented in dbt.
```
Python scripts → S3 (data lake) → Snowflake → dbt (Bronze → Silver → Gold) → Tableau
```

- **Bronze** — raw ingested data
- **Silver** — cleaned, standardized, and enriched datasets
- **Gold** — aggregated, analytics-ready data marts

## Synthetic Data Generation

All datasets are fully synthetic, generated using custom Python modules built on Faker and NumPy. The generators simulate realistic retail behaviour across 14 interconnected tables, incorporating:

- **Weighted probabilities** — location weights, traffic source distribution, device usage patterns
- **Customer personas** — 5 distinct personas driving differentiated purchasing behaviour
- **Business rules** — referential integrity enforced at generation time, documented in `elecmart-business-rules.md`
- **Realistic patterns** — seasonal trends, loyalty tier distribution, promotion uptake rates, clickstream-to-purchase conversion logic

Generated datasets are exported as Parquet files for efficient storage and downstream ingestion into S3 and Snowflake.

> The full data dictionary covering all 14 tables, column definitions, data types, and grain is available in `docs/data_dictionary/`.

---

## Data Model

Star schema with 4 fact tables and 10 dimension tables.

| Table | Type | Grain | Approx. rows |
|---|---|---|---|
| `fact_transaction` | Fact | One row per transaction | 2,500,000 |
| `fact_sale` | Fact | One row per line item per transaction | 1,600,000 |
| `fact_clickstream` | Fact | One row per web session | 17,000,000 |
| `inventory` | Fact | One row per store × product × month | 282,000 |
| `dim_date` | Dimension | One row per calendar date | 3,650 |
| `dim_customer` | Dimension | One row per customer | 200,000 |
| `dim_product` | Dimension | One row per SKU | 470 |
| `dim_store` | Dimension | One row per store | 50 |
| `dim_promotion` | Dimension | One row per promotion | 300 |
| `dim_campaign` | Dimension | One row per campaign | 500 |
| `dim_category` | Dimension | One row per category | 10 |
| `dim_subcategory` | Dimension | One row per subcategory | 28 |
| `dim_brand` | Dimension | One row per brand | 50 |
| `dim_location` | Dimension | One row per city | 25 |

---

## Key Metrics
```
Net Revenue         = SUM(transaction_total)
Profit          = Net_Revenue − Cost
Margin %        = Profit / Revenue
Avg daily sales = Units sold / Number of days
Inventory turns = Units sold / Average inventory
```

---

## Dashboards

Six Tableau dashboards consume the Gold layer:

- **Executive Dashboard** — tracks overall business performance including revenue trends, profit margins, top-performing products, and store-level performance.
- **Sales Dashboard** — analyzes customer segmentation, purchasing behavior, customer lifetime value (CLV), and purchase frequency trends.
- **Clickstream Dashboard** — monitors end-to-end user behavior including traffic sources, session journeys, funnel progression, and promotion effectiveness.
- **Customer Dashboard** — provides a holistic view of user journeys from visits → product views → cart → purchase, including device-level engagement patterns.
- **Clickstream Dashboard** — promotion effectiveness, traffic sources, conversion rates
- **Marketing Dashboard** — evaluates campaign and channel performance through attribution analysis, traffic quality, and conversion efficiency.
- **Inventory Dashboard** — tracks product demand dynamics, inventory movement, stock turnover, and category-level performance insights.

---

## Data Quality

Enforced via dbt tests:

- `not_null` on all primary and foreign keys
- `unique` constraints on surrogate keys
- Referential integrity tests across fact and dimension tables
- Custom validations: no negative inventory, no duplicate transactions, valid date ranges

---

## Project Structure
```
elecmart/
│
├── README.md
├── requirements.txt
├── .gitignore
│
│
│── raw/
│   ├── dim_brand.csv
│   ├── dim_category.csv
│   ├── dim_product.csv
│   └── dim_subcategory.csv
│
│
│
├── sql/
│   ├── ddl/
│   │   ├── dim_brand.sql
│   │   ├── dim_campaign.sql
│   │   ├── dim_category.sql
│   │   ├── dim_customer.sql
│   │   ├── dim_date.sql
│   │   ├── dim_location.sql
│   │   ├── dim_product.sql
│   │   ├── dim_promotion.sql
│   │   ├── dim_store.sql
│   │   ├── dim_subcategory.sql
│   │   ├── fact_clickstream.sql
│   │   ├── fact_sale.sql
│   │   ├── fact_transaction.sql
│   │   └── inventory.sql
│   │
├── sql/
│   ├── snowflake_ddl/
│   │   ├── dim_brand.sql
│   │   ├── dim_campaign.sql
│   │   ├── dim_category.sql
│   │   ├── dim_customer.sql
│   │   ├── dim_date.sql
│   │   ├── dim_location.sql
│   │   ├── dim_product.sql
│   │   ├── dim_promotion.sql
│   │   ├── dim_store.sql
│   │   ├── dim_subcategory.sql
│   │   ├── fact_clickstream.sql
│   │   ├── fact_sale.sql
│   │   ├── fact_transaction.sql
│   │   └── inventory.sql
│
│
├── src/
│   ├── __init__.py
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   ├── paths.py
│   │   ├── volumes.py
│   │   └── constants.py
│   │
│   ├── generators/
│   │   ├── __init__.py
│   │   ├── brands.py
│   │   ├── campaigns.py
│   │   ├── categories.py
│   │   ├── customers.py
│   │   ├── date.py
│   │   ├── fact_clickstream.py
│   │   ├── fact_sale.py
│   │   ├── campaigns.py
│   │   ├── fact_transaction.py
│   │   ├── inventory.py
│   │   ├── location.py
|   |   |── main.py
|   |   |── month_distribution.py
|   |   |── products.py
|   |   |── promotions.py
|   |   |── segment_customers.py
|   |   |── segment_stores.py
│   │   └── subcategories.py
|   |   
|   |── snowflake_setup/
|   |   ├── __init__.py
|   |   └── create_raw_tables.py
|   |
|   |
|   |── run_dbt/
|   |   ├── __init__.py
|   |   └── run_models.py
│   │
│   └── storage/
│       ├── __init__.py
│       ├── s3_upload.py
│       └── snowflake_upload.py
│
├── raw/
│    ├── dim_brand.csv
│    ├── dim_category.csv
│    ├── dim_subcategory.csv
│    └── dim_product.csv
│
└── elecmart/ (dbt)
    ├── analyses/
    ├── macros/
    │   └── generate_schema_name.sql
    ├── models/
    │   ├── BRONZE/
    │   │   └── sources.yml
    │   ├── SILVER/
    │   │   ├── dimension/
    │   │   │   ├── silver_dim_brand
    │   │   │   │   ├── tests/
    │   │   │   │   │    └── 
    │   │   │   │   ├── silver_dim_brand.sql
    │   │   │   │   └── silver_dim_brand.yml
    │   │   │   ├── silver_dim_campaign
    │   │   │   │   ├── tests/
    │   │   │   │   │    └── 
    │   │   │   │   ├── silver_dim_campaign.sql
    │   │   │   │   └── silver_dim_campaign.yml
    │   │   │   ├── silver_dim_category_subcategory
    │   │   │   │   ├── tests/
    │   │   │   │   │    └── 
    │   │   │   │   ├── silver_dim_category.sql
    │   │   │   │   ├── silver_dim_subcategory.sql
    │   │   │   │   └── cat_schema.yml
    │   │   │   ├── silver_dim_customer
    │   │   │   │   ├── tests/
    │   │   │   │   │    └── 
    │   │   │   │   ├── silver_dim_customer.sql
    │   │   │   │   └── silver_dim_customer.yml
    │   │   │   ├── silver_dim_date
    │   │   │   │   ├── tests/
    │   │   │   │   │    └── day_num_logic.sql
    │   │   │   │   ├── silver_dim_date.sql
    │   │   │   │   └── silver_dim_date.yml
    │   │   │   ├── silver_dim_location
    │   │   │   │   ├── tests/
    │   │   │   │   │    └── 
    │   │   │   │   ├── silver_dim_location.sql
    │   │   │   │   └── silver_dim_location.yml
    │   │   │   ├── silver_dim_product
    │   │   │   │   ├── tests/
    │   │   │   │   │    └── check_price_vs_cost.sql
    │   │   │   │   ├── silver_dim_product.sql
    │   │   │   │   └── silver_dim_product.yml
    │   │   │   ├── silver_dim_promotion
    │   │   │   │   ├── tests/
    │   │   │   │   │    └── 
    │   │   │   │   ├── silver_dim_promotion.sql
    │   │   │   │   └── silver_dim_promotion.yml
    │   │   │   └── silver_dim_store
    │   │   │   │   ├── tests/
    │   │   │   │   │    └── 
    │   │   │   │   ├── silver_dim_store.sql
    │   │   │   │   └── silver_dim_store.yml
    │   │   └── fact/
    │   │       ├── silver_fact_clickstream
    │   │       │   ├── tests/
    │   │       │   │    └── 
    │   │       │   ├── silver_fact_clickstream.sql
    │   │       │   └── silver_fact_clickstream.yml
    │   │       ├── silver_fact_inventory
    │   │       │   ├── tests/
    │   │       │   │    └── 
    │   │       │   ├── silver_fact_inventory.sql
    │   │       │   └── silver_fact_inventory.yml
    │   │       ├── silver_fact_sale
    │   │       │   ├── tests/
    │   │       │   │    └── 
    │   │       │   ├── silver_fact_sale.sql
    │   │       │   └── silver_fact_sale.yml
    │   │       └──silver_fact_transaction
    │   │           ├── tests/
    │   │           │    └── 
    │   │           ├── silver_fact_transaction.sql
    │   │           └── silver_fact_transaction.yml
    │   │
    │   │
    │   └── GOLD/
    │       
    ├── seeds
    ├── snapshots
    ├── tests
    ├── .user.yml
    ├── dbt_project.yml
    ├── profiles.yml
    └── README.md
```

---

## Setup

**Prerequisites:** Python 3.x · dbt · Snowflake account · AWS S3 credentials
```bash
git clone https://github.com/ajibola-komo/Elecmart-Retail-and-Ecommerce-Performance-Analytics.git
cd elecmart
pip install -r requirements.txt
```

Update `elecmart/.env` with your Snowflake and AWS credentials, then run:
```bash
python -m src.generators.main
```

---

## Author

**Ajibola Komolafe** — Data and Analytics Engineer (With Project Experience)
