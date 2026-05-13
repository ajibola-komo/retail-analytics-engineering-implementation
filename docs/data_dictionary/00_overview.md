# Elecmart Retail Analytics Pipeline – Overview

## Project Summary
This project simulates a modern retail analytics platform for a mid-sized electronics company, enabling end-to-end decision-making across:

- Sales performance
- Customer behavior
- Marketing attribution
- Inventory optimization

The 3-year dataset is synthetically generated using Python (Faker, NumPy) and modeled using a modern ELT stack:
- AWS Data Lake
- Snowflake (Data Warehouse)
- dbt (Transformation Layer)
- AWS EC2 (Compute Layer)

---

## Key Features

- 14 interconnected tables across domains
- Bronze → Silver → Gold architecture
- Star schema for BI optimization
- Embedded business rules and constraints
- dbt-powered data quality testing

---

## Analytical Use Cases

- Revenue and profitability analysis
- Customer segmentation
- Marketing funnel analytics
- Inventory planning and stock optimization