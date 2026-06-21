# Retail Analytics Engineering Project

## Overview

The Retail Analytics Engineering Platform is a production-grade analytics engineering project built to modernize and extend the capabilities of the original [ElecMart analytics solution](https://github.com/ajibola-komo/Elecmart-Retail-Analytics-Pipeline).

While the initial ElecMart project successfully delivered descriptive reporting for retail operations, it lacked the analytical depth, orchestration, and semantic modelling required to support advanced business intelligence and diagnostic analytics. This project addresses those limitations by rebuilding the analytics architecture from the ground up using modern analytics engineering principles.

The platform introduces a robust transformation layer, enhanced semantic models, automated orchestration workflows, and redesigned Power BI dashboards to create a scalable and maintainable analytics ecosystem capable of supporting both operational reporting and strategic decision-making.

## Project Objectives

The primary objectives of this project are:

* Redesign the semantic layer to support deeper diagnostic analytics and business investigation workflows
* Establish standardized business metrics and KPI definitions across the organization
* Implement production-ready data modelling practices using dbt
* Automate daily synthetic data generation and ingestion workflows using Apache Airflow
* Improve data quality, governance, testing, and documentation
* Rebuild executive and operational dashboards in Power BI using business-focused data marts
* Simulate a real-world analytics engineering environment with automated data pipelines and scheduled refreshes

## Business Problem

Retail organizations often struggle to move beyond descriptive reporting due to fragmented data models, inconsistent metric definitions, and tightly coupled reporting logic.

The original ElecMart solution provided visibility into key business metrics such as revenue, orders, products, and customers. However, it offered limited capability for answering deeper business questions such as:

* Why are sales declining in specific product categories?
* What factors contribute to customer churn?
* Which customer segments generate the highest lifetime value?
* What operational factors influence inventory performance?
* How do promotions impact customer purchasing behaviour?
* Which products drive repeat purchases and retention?

To answer these questions effectively, organizations require a well-designed semantic layer that enables drill-down analysis, dimensional slicing, and root-cause investigation.

This project focuses on building that analytical foundation.

## Solution Architecture

The platform consists of four major components:

### 1. Automated Data Generation

A Python-based synthetic data generation framework produces realistic retail business data including:

* Customers
* Transactions
* Sales
* Products
* Inventory
* Marketing campaigns
* Promotions
* Clickstreams
* Returns and refunds

### 2. Workflow Orchestration

Apache Airflow orchestrates the daily execution of the platform by:

* Generating new transactional data
* Loading files into cloud storage
* Triggering warehouse ingestion processes
* Running dbt transformation pipelines
* Executing data quality tests
* Refreshing analytics datasets

### 3. Analytics Engineering Layer

The transformation layer is built using dbt and follows a layered architecture:

* Staging Models
* Intermediate Models
* Core Business Models
* Dimensional Models
* Analytics Data Marts
* Semantic Layer Models

Key features include:

* Incremental processing
* Data quality testing
* Documentation generation
* Lineage tracking
* Reusable business logic
* Centralized KPI definitions

### 4. Business Intelligence Layer

Power BI dashboards are rebuilt using curated semantic models designed specifically for business investigation and decision support.

Dashboard areas include:

* Executive Performance Overview
* Revenue and Profitability Analysis
* Customer Analytics
* Product Performance Analysis
* Inventory and Supply Chain Analytics
* Marketing Performance Analytics
* Customer Retention and Cohort Analysis
* Root Cause and Diagnostic Analysis

## Key Enhancements Over the Original ElecMart Project

| Original ElecMart Project      | Retail Analytics Engineering Platform   |
| ------------------------------ | --------------------------------------- |
| Basic reporting layer          | Advanced semantic layer                 |
| Descriptive analytics          | Diagnostic analytics                    |
| Static data generation         | Automated daily data generation         |
| Manual execution               | Airflow orchestration                   |
| Dashboard-focused architecture | Analytics platform architecture         |
| Limited business dimensions    | Rich dimensional modelling              |
| Basic KPI calculations         | Centralized metric governance           |
| Minimal testing                | Production-grade data quality framework |
| Simple star schemas            | Business-oriented analytics marts       |
| Report consumption             | Investigation and decision support      |

## Technology Stack

* Python
* Apache Airflow
* dbt Core
* Snowflake
* Google Cloud Storage (GCS)
* SQL
* Power BI
* Git

## Expected Outcomes

By the completion of this project, the platform will demonstrate:

* Production-ready analytics engineering workflows
* Advanced dimensional modelling techniques
* End-to-end orchestration and automation
* Robust semantic layer design
* Diagnostic analytics capabilities
* Executive-ready business intelligence solutions
* Analytics engineering best practices used in modern data organizations
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
| `fact_transaction` | Fact | One row per transaction | ~900,000 |
| `fact_sale` | Fact | One row per line item per transaction | ~1,800,000 |
| `fact_clickstream` | Fact | One row per web session | ~14,000,000 |
| `fact_inventory` | Fact | One row per store × product × month | ~586,000 |
| `dim_date` | Dimension | One row per calendar date | ~3,650 |
| `dim_customer` | Dimension | One row per customer | ~150,000 |
| `dim_product` | Dimension | One row per SKU | 470 |
| `dim_store` | Dimension | One row per store | 50 |
| `dim_promotion` | Dimension | One row per promotion | 150 |
| `dim_campaign` | Dimension | One row per campaign | 120 |
| `dim_category` | Dimension | One row per category | 10 |
| `dim_subcategory` | Dimension | One row per subcategory | 28 |
| `dim_brand` | Dimension | One row per brand | 50 |
| `dim_location` | Dimension | One row per city | ~ 25 |

---

## Key Metrics
```
Net Revenue     = (SUM(net_line_revenue) WHERE transaction_status = 'Completed')
Profit          = Net_Revenue − Cost
Margin %        = Profit / Revenue
Avg daily sales = Units sold / Number of days
Inventory turns = Units sold / Average inventory
```
## Documentation

Full data dictionary, modeling decisions, and metric definitions:
[`docs/data_dictionary/`](docs/data_dictionary/)  
[Data dictionary PDF](docs/data_dictionary/data_dictionary.pdf)  
[Kaggle dataset](https://www.kaggle.com/datasets/ajibsss/elecmart-retail-analytics-dataset)

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
├── env_format
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
│   ├── ddl/ (duckdb table definition)
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
│   ├── snowflake_ddl/ (snowflake table definition)
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
│       └── inventory.sql
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
│   │   ├── fact_transaction.py
│   │   ├── inventory.py
│   │   ├── location.py
|   |   |── main.py
|   |   |── month_distribution.py
|   |   |── products.py
|   |   |── promotions.py
|   |   |── segment_customers.py
|   |   |── segment_stores.py
|   |   |── stores.py
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
├── docs/
│       ├── elecmart_business_rules.md
│       └──data_dictionary/
│            ├── 00_overview.md
│            ├── 01_data_lineage.md
│            ├── 02_modeling_strategy.md
│            ├── 03_dimensions.md
│            ├── 04_facts.md
│            ├── 05_metrics.md
│            ├── 06_data_quality.md
│            └── data_dictionary.pdf
│          ── architecture_diagrams/
│            ├── dbt-dag.png
│            ├── 
│            ├── 
│            ├── 
│            └──
│          ── metrics/
│            └──metrics_definition.md
│
│
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
    │   │       │   │    ├── campaign_id_to_traffic_source.sql
    │   │       │   │    └── funnel_logic.sql
    │   │       │   │                        
    │   │       │   ├── silver_fact_clickstream.sql
    │   │       │   └── silver_fact_clickstream.yml
    │   │       ├── silver_fact_inventory
    │   │       │   ├── silver_fact_inventory.sql
    │   │       │   └── silver_fact_inventory.yml
    │   │       ├── silver_fact_sale
    │   │       │   ├── silver_fact_sale.sql
    │   │       │   └── silver_fact_sale.yml
    │   │       └──silver_fact_transaction
    │   │           ├── silver_fact_transaction.sql
    │   │           └── silver_fact_transaction.yml
    │   │
    │   │
    │   └── GOLD/
    │   │   ├── dimensions/
    │   │   │   ├── gold_dim_campaign.sql
    │   │   │   │── gold_dim_customer.sql
    │   │   │   │── gold_dim_date.sql
    │   │   │   │── gold_dim_product.sql
    │   │   │   │── gold_dim_promotion.sql
    │   │   │   └── gold_dim_store.sql
    │   │   ├── facts/
    │   │   │   │── gold_fact_clickstream.sql
    │   │   │   │── gold_fact_inventory.sql
    │   │   │   │── gold_fact_sale.sql
    │   │   │   │── gold_fact_transaction.sql
    │   │   │   └── schema.yml
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

**Prerequisites:** Python 3.x · dbt · Snowflake account · AWS S3 credentials · AWS EC2 Instance 
- create an S3 bucket called 'elecmart-bucket'
    - Create IAM credentials
    - Configure AWS CLI locally
    - Update your `elecmart/.env` file with your AWS credentials
- create an EC2 instance with the following configurations:
    - **Amazon Machine Image** - Ubuntu Server 24.04 LTS (HVM), SSD Volume Type
    - **Architecture** - 64-bit (x86)
    - **Instance Type** - r6i.xlarge
    - **Key Pair** - Create a new key pair type .pem or use your existing formats
    - Download the .pem file
    - **Configure Storage** - 1x 100 GiB gp3

- Connect to your EC2 instance through VSCode

```bash
git clone https://github.com/ajibola-komo/Elecmart-Retail-and-Ecommerce-Performance-Analytics.git
cd Elecmart-Retail-Analytics-Pipeline
sudo apt update
sudo apt upgrade -y
sudo apt autoremove -y
sudo apt install python3-venv -y
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
source venv/bin/activate
mkdir -p data/parquet/exports
```
Create `.env` file using the format from `env_format`
Update `Elecmart-Retail-Analytics-Pipeline/.env` with your Snowflake and AWS credentials, then run:
```bash
python -m src.generators.main
```
---

## Author

**Ajibola Komolafe** — Data and Analytics Engineer
[LinkedIn](https://www.linkedin.com/in/ajibola-k-4ba921123/) · [GitHub](https://github.com/ajibola-komo) ·
[Tableau](https://public.tableau.com/app/profile/ajibola.komolafe/viz/Elecmart_17786325127340/ExecutiveDashboard?publish=yes) · [Kaggle Dataset](https://www.kaggle.com/datasets/ajibsss/elecmart-retail-analytics-dataset)
