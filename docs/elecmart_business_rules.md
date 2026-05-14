# Elecmart — Business Rules & Analytics Framework

> **Last Updated:** May 2026

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Business Definitions (Source of Truth)](#2-business-definitions-source-of-truth)
3. [Data Generation Framework (Simulation Rules)](#3-data-generation-framework-simulation-rules)
4. [Dimensional Modelling Framework](#4-dimensional-modelling-framework)
5. [Marketing & Funnel Analysis Framework](#5-marketing--funnel-analysis-framework)
6. [Business Metric Definitions](#6-business-metric-definitions)
7. [Design Principles](#7-design-principles)
8. [Conclusion](#8-conclusion)
9. [Document Ownership](#9-document-ownership)
10. [Data Refresh & Cadence](#10-data-refresh-and-cadence)

---

## 1. Executive Summary

This document defines the business logic, data generation framework, dimensional modelling approach, and analytics definitions for the Elecmart project.

Elecmart simulates a modern retail and e-commerce business, enabling analysis across:

- Sales & profitability
- Customer behavior
- Marketing performance
- Inventory management

The framework is designed to:

- Reflect real-world retail operations
- Support scalable analytics in Snowflake
- Power Tableau dashboards (executive + operational)

---

## 2. Business Definitions (Source of Truth)

> This section defines how the business interprets data, independent of implementation.

### 2.1 Transactions & Sales

A **transaction** represents a single purchase event. A **sale** contains multiple line items (products).

Transactions can occur via:

- Online (Web / Mobile)
- Physical store

**Transaction statuses:**

| Status | Description |
|---|---|
| `Completed` | Successful sale |
| `Returned` | Reversal of a completed sale |

### 2.2 Revenue

| Term | Definition |
|---|---|
| **Gross Revenue** | Total value of goods sold after discount and before returns |
| **Net Revenue** | Revenue after discounts and returns |

> Returned transactions reduce gross revenue.

### 2.3 Customer

A **customer** is an individual who interacts with the business. Customers may be:

- **Active Customers (identified)** — linked to a `customer_id`
- **Guest (anonymous)** — session-only interaction

### 2.4 Promotions & Campaigns

- A **promotion** represents a discount applied to a transaction.
- A **campaign** represents a marketing effort that may or may not include a promotion.
- A transaction can have **at most one promotion**.
- Campaigns drive traffic, engagement, and conversion.

### 2.5 Inventory

Inventory reflects stock levels per **product × store × time period (month end)**, tracked using monthly snapshots.

---

## 3. Data Generation Framework (Simulation Rules)

> This section defines how synthetic data is created. These are **simulation rules**, not business definitions.

### 3.1 General

- Data is generated using **Python** (Faker, NumPy)
- Deterministic via random seed
- Stored as **Parquet** → Stored on AWS S3 → ingested into Snowflake
- Business constraints enforced at generation time

### 3.2 Dates

- **Simulation window:** 30 May 2001 → Present Year - 1 (~20+ years)
- Date keys use `YYYYMMDD` integer format
- All fact records reference valid date keys
- Inventory month references use a month_id field in `YYYYMM` format

### 3.3 Customers

- **Total customers:** 150,000
- **Minimum age:** 18 years
- Each customer is assigned a **persona**

Personas drive:

- Purchase frequency
- Average order value (AOV)
- Loyalty tier

#### 3.3.1 Persona Definition
- **Tech Enthusiast:** Makes up approximately 20% of customers, age range (25 - 40). This customer segment generates the highest revenue with  the highest repeat purchase rates. 
- **Bargain Hunter:** Makes up approximately 25% of customers, age range (18 - 35). This segment is more likely to purchase when there is a discount attached.
- **Practical Buyer:** Makes up approximately 10% of customers, age range (30,60). This segment is more likely to purchase when there is a discount attached.
- **Gift Shopper:** Makes up approximately 5% of customers, age range (28 - 45). This is your occasional shopper, not necessarily driven by discount.
- **Everyday Shopper:** Makes up approximately 40% of customers, age range (30 - 50). This customer segment has the highest contribution to volume but the second highest contribution to revenue because it has a lower AOV compared to the **Tech Enthusiast**.

### 3.4 Products

~470 SKUs across:

- 10 categories
- 28 subcategories
- ~50 brands

**Rules:**

- `unit_price > unit_cost`
- Valid category hierarchy enforced
- Price segments defined (Low → Flagship)

### 3.5 Stores

- **Total stores:** 50
- **Store types:** Mall, Standalone, Outlet, Warehouse
- Opening date precedes all transactions
- Store weights model Canada's population distribution to increase data realism

### 3.6 Transactions & Sales

- **~900,000 transactions**
- **~1.8M line items**

Each transaction references:

| Field | Required |
|---|---|
| `store_id` | ✅ Always |
| `transaction_date_id` | ✅ Always |
| `customer_id` | Optional (registered customers only i.e. non-anonymous transactions) |
| `session_id` | Optional (online only) |
| `campaign_id` | Optional (campaign linked transactions only) |
| `promo_id` | Optional (campaign and promotion linked transactions only) |

**Calculations:**

```
transaction_total = transaction_subtotal − transaction_discount_applied
line_total        = unit_price × quantity
line_cost         = unit_cost  × quantity
```

**Returns:**

- Represent reversal events
- `Completed` → positive revenue
- `Returned` → negative revenue

### 3.7 Clickstream (Simulation Logic)

> ⚠️ These are simulation assumptions, not business rules.

- **~14M sessions**
- **~35%** anonymous users

**Funnel probabilities:**

| Stage | Probability |
|---|---|
| Product View → Add to Cart | ~ 40% |
| Add to Cart → Purchase | ~ 30% |

### 3.8 Promotions & Campaigns

- **~150 promotions across 3 years**
- **~120 campaigns across 3 years**

**Rules:**

- One promotion per transaction (max)
- Campaigns may exist without promotions
- Discount constraints enforced — only transactions **> 50 CAD** are eligible for discounts
- Only online transactions can be attributed to a campaign and marketing effort

### 3.9 Inventory

**Grain:** Product × Store × Month

**Formula:**

```
closing_stock = starting_stock + received_stock − sold_units − shrinkage_loss
```

**Constraints:**

- No negative inventory
- Backorders flagged when demand exceeds supply

---

## 4. Dimensional Modelling Framework

### 4.1 Modelling Approach

- Kimball **star schema**
- Conformed dimensions
- Surrogate keys for all dimensions

### 4.2 Fact Table Grain

| Table | Grain |
|---|---|
| `fact_transaction` | 1 row per transaction |
| `fact_sale` | 1 row per transaction line item |
| `fact_clickstream` | 1 row per session |
| `fact_inventory` | 1 row per product × store × month |

### 4.3 Dimension Tables

| Dimension | Description |
|---|---|
| `dim_date` | Daily with associated month_id field in the format `(YYYYMM)` |
| `dim_brand` | Brand Details |
| `dim_category` | Category Details |
| `dim_subcategory` | SubCategory Details |
| `dim_customer` | Customer attributes |
| `dim_product` | Product attributes |
| `dim_store` | Store attributes |
| `dim_location` | Location hierarchy |
| `dim_campaign` | Campaign details |
| `dim_promotion` | Promotion details |

### 4.4 Referential Integrity

- All foreign keys enforced
- Nullable relationships explicitly defined
- Inventory uses `snapshot_month_id` → `dim_date (month_id)`

### 4.5 Modelling Constraints

- No Slowly Changing Dimensions (SCD)
- Derived attributes precomputed
- Generation-only fields excluded from Gold layer

---

## 5. Marketing & Funnel Analysis Framework

### 5.1 Funnel Definition

The Elecmart model supports a digital conversion funnel tracking user progression:

```
Session → Product View → Add to Cart → Purchase → Transaction
```

### 5.2 Funnel Stages

| Stage | Definition |
|---|---|
| **Session** | User visits site |
| **Product View** | Visits product page |
| **Add to Cart** | Adds item to cart |
| **Purchase** | Completes transaction |

### 5.3 Funnel Rules

- Each stage depends on the previous stage
- Funnel is sequential and hierarchical
- All purchases originate from sessions

### 5.4 Funnel Metrics

| Metric | Formula |
|---|---|
| **Product View Rate** | Product Views / Sessions |
| **Add-to-Cart Rate** | Add to Cart / Product Views |
| **Conversion Rate** | Purchases / Sessions |
| **Cart Abandonment Rate** | (Add to Cart − Purchases) / Add to Cart |
| **Bounce Rate** | Sessions with less than 2 page views / Total Sessions |

### 5.5 Marketing Attribution

**Attribution Rules:**

- Sessions may be linked to campaigns via `campaign_id`
- Transactions are attributed when:
  - Linked to a campaign session, **AND**
  - `campaign_id` exists on the transaction

### 5.6 Campaign Metrics

| Metric | Definition |
|---|---|
| **Campaign Sessions** | Sessions with `campaign_id` |
| **Campaign Conversion Rate** | Purchases / Campaign Sessions |
| **Campaign Revenue** | Revenue from attributed transactions |
| **Total Promotions Applied** | Transactions with promotion |

### 5.7 Traffic Source Analysis

Traffic is segmented into:

- Organic
- Paid Search
- Direct
- Referral
- Campaign

---

## 6. Business Metric Definitions

All business metrics and KPI definitions can be found on `docs/metrics/metrics_definition.md`

---

## 7. Design Principles

- Business definitions **precede** technical implementation
- Fact tables strictly adhere to grain
- Dimensions are reusable and consistent
- Metrics are standardized across all layers
- Simulation logic is clearly separated from business logic

---

## 8. Conclusion

This framework enables:

- End-to-end analytics across sales, marketing, and operations
- Scalable reporting in Snowflake + Tableau
- Realistic simulation of retail and e-commerce behavior

---
## 9. Document Ownership
This document is authored and maintained by [Ajibola Komolafe](https://www.linkedin.com/in/ajibola-k-4ba921123/) as part of a solo portfolio project. All business rules, simulation logic, and metric definitions reflect intentional design decisions made by the author.

---
## 10. Data Refresh and Cadence
As a static simulation dataset, the underlying data does not refresh automatically. In a production deployment, the recommended cadence would be:
- **Transactional facts (sales, clickstream):** daily batch load
- **Inventory snapshots:** monthly, aligned to month-end grain
- **Dimension tables:** on-change, with a nightly consistency check

This document should be updated whenever business rules or metric definitions change.

---

## Project Links
[LinkedIn](https://www.linkedin.com/in/ajibola-k-4ba921123/) · [GitHub](https://github.com/ajibola-komo) ·
[Tableau](https://public.tableau.com/app/profile/ajibola.komolafe/viz/Elecmart_17786325127340/ExecutiveDashboard?publish=yes) · [Kaggle Dataset](https://www.kaggle.com/datasets/ajibsss/elecmart-retail-analytics-dataset)

