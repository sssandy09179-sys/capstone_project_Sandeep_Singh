# Mamaearth Returns & Growth Intelligence Pipeline

An end-to-end data pipeline combining SQL relational modeling,
pandas data wrangling, exploratory data analysis (EDA),
and GenAI narrative generation to diagnose high return rates and uncover revenue trends for Mamaearth's Growth and Regional Ops teams.

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
