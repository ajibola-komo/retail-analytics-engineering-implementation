# Elecmart — Business Metrics Definition

> **Last Updated:** May 2026
> **Source Tables:** `gold_fact_sale`, `gold_fact_transaction`, `gold_fact_inventory`, `gold_fact_clickstream`

---

## Table of Contents

1. [Revenue & Profitability](#1-revenue--profitability)
2. [Sales Performance](#2-sales-performance)
3. [Return Metrics](#3-return-metrics)
4. [Inventory Metrics](#4-inventory-metrics)
5. [Customer Metrics](#5-customer-metrics)
6. [Marketing & Funnel Metrics](#6-marketing--funnel-metrics)

---

## 1. Revenue & Profitability

**Source Table:** `gold_fact_sale`

| Metric | Business Definition | SQL Logic | Notes |
|---|---|---|---|
| **Gross Revenue** | Total revenue after discounts before accounting for returns | `SUM(net_line_revenue)` | Includes both completed and returned transactions |
| **Net Revenue** | Revenue from successfully completed transactions | `SUM(net_line_revenue) WHERE transaction_status = 'Completed'` | Primary revenue KPI |
| **COGS** | Cost of goods sold for completed transactions | `SUM(line_cost) WHERE transaction_status = 'Completed'` | Excludes returned transactions |
| **Gross Profit** | Profit after cost of goods sold | `Net Revenue - COGS` | Core profitability metric |
| **Gross Margin %** | Profitability as a percentage of revenue | `Gross Profit / Net Revenue` | Key margin indicator |

---

## 2. Sales Performance

**Source Table:** `gold_fact_sale`

| Metric | Business Definition | SQL Logic | Notes |
|---|---|---|---|
| **Total Transactions** | Number of completed purchase events | `COUNT(DISTINCT transaction_id) WHERE transaction_status = 'Completed'` | Excludes returned transactions |
| **Returned Transactions** | Number of returned purchase events | `COUNT(DISTINCT transaction_id) WHERE transaction_status = 'Returned'` | Excludes completed transactions |
| **Total Orders** | All transactions regardless of outcome | `COUNT(DISTINCT transaction_id)` | Includes returned transactions |
| **Units Sold** | Total quantity of items successfully sold | `SUM(quantity) WHERE transaction_status = 'Completed'` | Net of returns |
| **Units Returned** | Total quantity of returned items | `SUM(quantity) WHERE transaction_status = 'Returned'` | Helps track product issues |
| **Average Order Value (AOV)** | Average revenue per completed transaction | `Net Revenue / Total Transactions` | Based on completed orders only |

---

## 3. Return Metrics

**Source Table:** `gold_fact_sale`

| Metric | Business Definition | SQL Logic | Notes |
|---|---|---|---|
| **Returned Revenue** | Value of transactions that were returned | `SUM(net_line_revenue) WHERE transaction_status = 'Returned'` | Derived from sales table |
| **Return Rate %** | Percentage of revenue that was returned | `Returned Revenue / Gross Revenue` | Indicates product or service issues |
| **Return Transaction Rate %** | Percentage of transactions that were returned | `Returned Transactions / Total Orders` | Operational quality metric |

---

## 4. Inventory Metrics

**Source Table:** `gold_fact_inventory` — Monthly grain (Product × Store × Month)

| Metric | Business Definition | SQL Logic | Notes |
|---|---|---|---|
| **Inventory Turnover** | Stock efficiency | `SUM(sold_units) / AVG((starting_stock + closing_stock) / 2.0)` | Performance metric |
| **Total Shrinkage Loss** | Value of inventory lost to theft, damage, or administrative error | `SUM(shrinkage_loss)` | Operational risk metric; high values may indicate warehouse or store-level issues |
| **Total Units Sold** | Total quantity of units sold across all transactions | `SUM(sold_units)` | Base volume metric; used as denominator in sell-through and conversion rate calculations |
| **Total Units Received** | Total quantity of inventory received into stock from suppliers or transfers | `SUM(received_stock)` | Supply chain metric; paired with `sold_units` to derive closing stock reconciliation |

---

## 5. Customer Metrics

**Source Table:** `gold_fact_transaction` — Monthly grain

| Metric | Business Definition | SQL Logic | Notes |
|---|---|---|---|
| **Active Customers** | Customers with at least one completed purchase | `COUNT(DISTINCT customer_id) WHERE transaction_status = 'Completed' AND customer_id IS NOT NULL` | Core base metric; denominator for all customer-level ratios |
| **Repeat Customer Rate** | Percentage of active customers who have made more than one purchase | `COUNT(DISTINCT customer_id HAVING COUNT(*) > 1) / COUNT(DISTINCT customer_id)` | Loyalty indicator; low values suggest weak retention |
| **Purchase Frequency** | Average number of completed orders per active customer | `COUNT(DISTINCT transaction_id) / COUNT(DISTINCT customer_id)` | Engagement metric; rising trend signals stronger customer habits |
| **Average Revenue per Customer** | Average total revenue generated per active customer | `SUM(transaction_total WHERE transaction_status = 'Completed') / COUNT(DISTINCT customer_id WHERE customer_id IS NOT NULL AND transaction_status = 'Completed')` | Monetisation metric; used alongside Purchase Frequency to distinguish high-value vs. high-frequency segments |

---

## 6. Marketing & Funnel Metrics

**Source Tables:** `gold_fact_clickstream` (session metrics), `gold_fact_transaction` (campaign & promotion metrics) — Monthly grain

### 6.1 Funnel Metrics

| Metric | Business Definition | SQL Logic | Notes |
|---|---|---|---|
| **Total Sessions** | Total number of website visits recorded | `COUNT(DISTINCT session_id)` | Top-of-funnel metric; baseline denominator for all session-level rates |
| **Conversion Rate %** | Percentage of sessions that result in a completed purchase | `COUNT(DISTINCT session_id WHERE purchased_flag = TRUE) / COUNT(DISTINCT session_id)` | Core performance KPI; primary measure of funnel effectiveness |
| **Add-to-Cart Rate %** | Percentage of product page sessions where the customer added an item to cart | `COUNT(DISTINCT session_id WHERE added_to_cart_flag = TRUE) / COUNT(DISTINCT session_id WHERE product_page_visited_flag = TRUE)` | Measures purchase intent; declining trend may indicate pricing or UX friction |
| **Bounce Rate %** | Percentage of sessions where fewer than 2 pages were viewed | `COUNT(DISTINCT session_id WHERE number_of_pages_viewed < 2) / COUNT(DISTINCT session_id)` | Engagement quality indicator; high values suggest poor landing page relevance or slow load times |
| **Cart Abandonment %** | Percentage of sessions with cart activity that did not result in a purchase | `(COUNT(DISTINCT session_id WHERE added_to_cart_flag = TRUE) - COUNT(DISTINCT session_id WHERE purchased_flag = TRUE)) / COUNT(DISTINCT session_id WHERE added_to_cart_flag = TRUE)` | Friction indicator; high values suggest checkout barriers such as shipping cost or payment issues |

### 6.2 Campaign & Promotion Metrics

| Metric | Business Definition | SQL Logic | Notes |
|---|---|---|---|
| **Campaign Revenue** | Total revenue from completed transactions attributed to a marketing campaign | `SUM(transaction_total WHERE transaction_status = 'Completed' AND campaign_id IS NOT NULL)` | Attribution metric; excludes organic and unattributed transactions |
| **Revenue Attributed to Campaigns %** | Percentage of total completed revenue attributable to a marketing campaign | `SUM(transaction_total WHERE transaction_status = 'Completed' AND campaign_id IS NOT NULL) / SUM(transaction_total WHERE transaction_status = 'Completed')` | Marketing efficiency indicator; rising share suggests campaigns are driving incremental revenue |
| **Total Campaigns Run** | Total number of distinct campaigns active within the reporting period | `COUNT(DISTINCT campaign_id WHERE campaign_id IS NOT NULL)` | Campaign volume metric; context metric for normalising campaign revenue and attribution rates |
| **Total Promotions Applied** | Total number of completed transactions where a promotional code was applied | `COUNT(DISTINCT transaction_id WHERE promo_id IS NOT NULL)` | Promotion uptake metric; use alongside Avg Revenue per Promo Transaction to assess discount effectiveness |
| **Avg Revenue per Promo Transaction** | Average revenue generated per completed transaction where a promotion was applied | `SUM(line_total WHERE promo_id IS NOT NULL AND transaction_status = 'Completed') / COUNT(DISTINCT transaction_id WHERE promo_id IS NOT NULL AND transaction_status = 'Completed')` | Discount effectiveness metric; compare against non-promo avg revenue to assess margin impact |

---

## Authour
Ajibola Komolafe - Data Analyst & Analytics Engineer
[LinkedIn](https://www.linkedin.com/in/ajibola-k-4ba921123/)

## Project Links
[GitHub](https://github.com/ajibola-komo) · [Tableau](https://public.tableau.com/app/profile/ajibola.komolafe/viz/Elecmart_17786325127340/ExecutiveDashboard?publish=yes) · [Kaggle Dataset](https://www.kaggle.com/datasets/ajibsss/elecmart-retail-analytics-dataset)
