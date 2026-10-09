# Mamaearth Returns & Growth Intelligence Pipeline



An end-to-end data pipeline combining SQL relational modeling, pandas data wrangling, exploratory data analysis (EDA), and GenAI narrative generation to diagnose return rate patterns and quantify revenue trends for Mamaearth's Growth and Regional Ops teams.



---



## Repository Structure



```text

├── README.md

├── sql/

│   ├── schema.sql

│   ├── seed_data.sql

│   └── reports.sql

├── data/

│   ├── customers.csv

│   ├── products.csv

│   └── orders.csv

├── analysis/

│   ├── clean_and_eda.py

│   └── visualize.py

├── visualizations/

│   ├── return_rate_by_payment.png

│   └── monthly_revenue_trend.png

└── narrator/

    ├── findings.json

    └── generate_narrative.py

```



---



## Pipeline Execution Order



To reproduce every statistical metric, report table, chart, and executive narrative identically from scratch, execute the pipeline sequentially through the three layers below:



### Layer 1: SQL Relational Store & Reporting

The relational layer builds the normalized database structure and executes business reporting queries:



1. **Initialize Database Schema & Load Seed Data:**

   Run SQLite against the raw seed datasets in `data/`:

   ```bash

   # Create tables with constraints and foreign keys

   sqlite3 mamaearth.db < sql/schema.sql



   # Load seed datasets (customers, products, orders)

   sqlite3 mamaearth.db < sql/seed_data.sql

   ```

   *Note on NULL handling:* `sql/seed_data.sql` converts empty string cells in `discount_pct` and `rating` to SQL `NULL` so that statistical aggregates remain exact.



2. **Run SQL Reports:**

   ```bash

   sqlite3 mamaearth.db < sql/reports.sql

   ```

   *Expected report metrics:*

   - **Report (a) Order totals:** `total_orders = 180`, `total_revenue = 99860.20`, `avg_order_value = 554.78`.

   - **Report (b) Missing ratings:** `(180, 165, 15)` — 15 orders have no rating.

   - **Report (c) Zero-order customer:** Customer `C045` (Vihaan) verified by both `LEFT JOIN ... HAVING COUNT = 0` and `NOT IN` subquery.

   - **Report (d) City return rates (>20%):** Jaipur (42.1%), Lucknow (30.6%), Bangalore (24.2%).

   - **Report (e) Top spenders:** Top customer `C043` (Reyansh, INR 12,920.00); rank 3–5 offset slice returns `C008`, `C011`, and `C042`.

   - **Report (f) Category revenue:** Haircare (INR 44,956.10), Skincare (INR 27,346.00), Babycare (INR 16,805.00), PersonalCare (INR 10,753.10).



---



### Layer 2: Python Data Wrangling & Visualizations

An independent pandas pipeline running directly against the raw CSV files (`data/customers.csv`, `data/products.csv`, `data/orders.csv`):



1. **Execute Data Cleaning & Exploratory Data Analysis:**

   ```bash

   python analysis/clean_and_eda.py

   ```

   - Standardizes `payment_method` casing to `CARD` (70), `UPI` (55), and `COD` (55).

   - Drops exactly 5 duplicate order rows (`O0176`–`O0180`), reducing row count from 180 to 175.

   - Imputes missing `discount_pct` with 0 (12 rows) and missing `rating` with median 3.0 (15 rows).

   - Reconciles total revenue: Cleaned revenue is **INR 97,358.30**, which is exactly INR 2,501.90 lower than Part 1's INR 99,860.20, attributed strictly to the 5 dropped duplicates.

   - Detects quantity outliers (`O0011` with qty 25, `O0098` with qty 30) via IQR bounds `[-0.5, 3.5]`.

   - Confirms return rate hypothesis: COD stands at **44.4%** (~3x Card at 14.7%).

   - Identifies high-risk segment: **COD + Tier-2 cities at 54.5%** return rate.

   - Isolates monthly revenue trend: January drops from INR 29,582.10 to INR 11,637.10 when outliers are removed, proving **March (INR 20,318.90)** is the true peak sales month.

   - **Automated Hand-off:** Task 5 of this analysis layer automatically serializes and writes the verified summary metrics into **`narrator/findings.json`** for Layer 3.



2. **Generate Visualizations:**

   ```bash

   python analysis/visualize.py

   ```

   - Re-runs from raw CSVs and exports two charts into `visualizations/`:

     1. `visualizations/return_rate_by_payment.png`: Bar chart of return rate by payment method (descending) with exact bar labels and finding title.

     2. `visualizations/monthly_revenue_trend.png`: Line chart of outlier-corrected monthly revenue identifying March as the peak month.



---



### Layer 3: GenAI Executive Narrative Generation

Consumes verified figures from `narrator/findings.json` to produce an executive Situation-Complication-Resolution (SCR) report:



#### Execution Path A: Online Mode (Gemini API)

Set your Gemini API key in the shell environment and execute the script:

```bash

export GEMINI_API_KEY="your_api_key_here"

python narrator/generate_narrative.py

```

*(On Google Colab, store the key in Colab Secrets as `GEMINI_API_KEY`.)*



#### Execution Path B: Offline Mode (Deterministic Fallback)

If no Gemini API key is configured or external connectivity is unavailable, the script executes via a deterministic offline template fallback without making network calls:

```bash

unset GEMINI_API_KEY

python narrator/generate_narrative.py

```

Both execution paths generate the complete narrative and save it directly to **`narrator/sample_output.txt`**.



---



## Numerical Verification Checklist



| Metric Description | Raw / Expected Value | Cleaned / Outlier-Corrected Value |

| :--- | :--- | :--- |

| **Total Orders** | 180 rows | 175 rows (5 duplicates dropped) |

| **Total Revenue** | INR 99,860.20 | INR 97,358.30 (Delta: INR 2,501.90) |

| **COD Return Rate** | — | 44.4% (Card: 14.7%, UPI: 18.9%) |

| **Highest Risk Segment** | — | COD + Tier-2 Cities (54.5%) |

| **True Peak Month** | January (INR 29,582.10, outlier-inflated) | March (INR 20,318.90, outlier-corrected) |
