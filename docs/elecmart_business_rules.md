# Elecmart — Business Rules & Analytics Framework

> **Last Updated:** April 2026

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
| **Gross Revenue** | Total value of goods sold before discounts |
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
- **Bargain Hunter & Practical Buyer:** Makes up approximately 25% and 10% of customers respectively, age range (18 - 35) and (30,60). This segment is more likely to purchase when there is a discount attached.
- **Gift Shopper:** Makes up approximately 5% of customers, age range (28 - 45). This is your occassional shopper, not necessarily driven by doscount.
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
| `dim_date` | Daily |
| `dim_month` | Monthly |
| `dim_customer` | Customer attributes |
| `dim_product` | Product attributes |
| `dim_store` | Store attributes |
| `dim_location` | Location hierarchy |
| `dim_campaign` | Campaign details |
| `dim_promotion` | Promotion details |

### 4.4 Referential Integrity

- All foreign keys enforced
- Nullable relationships explicitly defined
- Inventory uses `snapshot_month_id` → `dim_month`

### 4.5 Modelling Constraints

- No Slowly Changing Dimensions (SCD)
- Derived attributes precomputed
- Generation-only fields excluded from Gold layer

---

## 5. Marketing & Funnel Analysis Framework

### 5.1 Funnel Definition

The Elecmart model supports a digital conversion funnel tracking user progression:

```
Session → Product View → Add to Cart → Purchase
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
| **Bounce Rate** | (Number of Pages Viewed < 2>) / Total Sessions |

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

### 6.1 Revenue & Profitability

| Metric | Business Definition | SQL Logic | Grain | Notes |
|---|---|---|---|---|
| **Gross Revenue** | Total revenue before accounting for returns | `SUM(net_line_revenue)` | Any | Includes both completed and returned transactions |
| **Net Revenue** | Revenue from successfully completed transactions | `SUM(net_line_revenue) WHERE transaction_status = 'Completed'` | Any | Primary revenue KPI |
| **Returned Revenue** | Revenue associated with returned transactions | `SUM(net_line_revenue) WHERE transaction_status = 'Returned'` | Any | Represents reversed revenue |
| **COGS** | Cost of goods sold for completed transactions | `SUM(line_cost) WHERE transaction_status = 'Completed'` | Any | Excludes returned transactions |
| **Gross Profit** | Profit after cost of goods sold | `Net Revenue - COGS` | Any | Core profitability metric |
| **Gross Margin %** | Profitability as a percentage of revenue | `Gross Profit / Net Revenue` | Any | Key margin indicator |

### 6.2 Sales Performance

| Metric | Business Definition | SQL Logic | Grain | Notes |
|---|---|---|---|---|
| **Total Transactions** | Number of completed purchase events | `COUNT(DISTINCT transaction_id) WHERE transaction_status = 'Completed'` | Any | Excludes returned transactions |
| **Total Orders (All)** | All transactions regardless of outcome | `COUNT(DISTINCT transaction_id)` | Any | Includes returned transactions |
| **Units Sold** | Total quantity of items successfully sold | `SUM(quantity) WHERE transaction_status = 'Completed'` | Any | Net of returns |
| **Units Returned** | Total quantity of returned items | `SUM(quantity) WHERE transaction_status = 'Returned'` | Any | Helps track product issues |
| **Average Order Value (AOV)** | Average revenue per completed transaction | `Net Revenue / Total Transactions` | Any | Based on completed orders only |

### 6.3 Returns Metrics

| Metric | Business Definition | SQL Logic | Grain | Notes |
|---|---|---|---|---|
| **Returned Revenue** | Value of transactions that were returned | `SUM(net_line_revenue) WHERE transaction_status = 'Returned'` | Any | Derived from sales table |
| **Return Rate %** | Percentage of revenue that was returned | `Returned Revenue / Gross Revenue` | Any | Indicates product or service issues |
| **Return Transaction Rate %** | Percentage of transactions that were returned | `Returned Transactions / Total Orders` | Any | Operational quality metric |

### 6.4 Inventory

| Metric | Business Definition | SQL Logic | Grain | Notes |
|---|---|---|---|---|
| **Inventory Turnover** | Stock efficiency | `Units Sold / Avg Inventory` | Monthly | Performance metric |
| **Stockout Rate** | % out-of-stock events | `Stockout flags / total records` | Monthly | Supply issue |

### 6.5 Customer Metrics

| Metric | Business Definition | SQL Logic | Grain | Notes |
|---|---|---|---|---|
| **Customer Lifetime Value (CLV)** | Total revenue generated per customer | `SUM(net_line_revenue) WHERE transaction_status = 'Completed' GROUP BY customer_id` | Customer | Long-term value metric |
| **Active Customers** | Customers with at least one completed purchase | `COUNT(DISTINCT customer_id) WHERE transaction_status = 'Completed'` | Any | Core base metric |
| **Repeat Customer Rate** | Percentage of customers with multiple purchases | `Customers with >1 transaction / Active Customers` | Customer | Loyalty indicator |
| **Purchase Frequency** | Average number of orders per customer | `Total Transactions / Active Customers` | Period | Engagement metric |

### 6.6 Marketing & Funnel Metrics

| Metric | Business Definition | SQL Logic | Grain | Notes |
|---|---|---|---|---|
| **Total Sessions** | Total number of website visits | `COUNT(session_id)` | Session | Top-of-funnel metric |
| **Conversion Rate %** | Percentage of sessions that result in a purchase | `Completed Transactions / Sessions` | Session | Core performance KPI |
| **Add-to-Cart Rate %** | Sessions with cart activity | `Add-to-Cart Events / Product Page Views` | Session | Measures intent |
| **Cart Abandonment %** | Users who abandon cart | `(Add-to-Cart - Purchases) / Add-to-Cart` | Session | Friction indicator |
| **Campaign Revenue** | Revenue attributed to marketing campaigns | `SUM(net_line_revenue) WHERE transaction_status = 'Completed' AND campaign_id IS NOT NULL` | Any | Attribution metric |

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

## Author

**Ajibola Komolafe** — Data and Analytics Engineer
[LinkedIn](https://www.linkedin.com/in/ajibola-k-4ba921123/) · [GitHub](https://github.com/ajibola-komo) ·
[Tableau](https://public.tableau.com/app/profile/ajibola.komolafe/viz/Elecmart_17786325127340/ExecutiveDashboard?publish=yes) · [Kaggle Dataset](https://www.kaggle.com/datasets/ajibsss/elecmart-retail-analytics-dataset)

