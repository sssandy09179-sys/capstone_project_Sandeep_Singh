
Task 1 — Load and inspect
"""

import pandas as pd

orders = pd.read_csv('orders.csv')
customers = pd.read_csv('customers.csv')
products = pd.read_csv('products.csv')

#print(orders.shape)

"""Task 2 — Standardize payment_method casing"""

#print(orders['payment_method'].unique())

orders['payment_method'] = orders['payment_method'].str.strip().str.upper()

#print(orders['payment_method'].value_counts())


"""Task 3 — Remove duplicate orders"""

natural_key = [
    'customer_id', 'product_id', 'order_date', 'quantity',
    'discount_pct', 'payment_method', 'rating', 'returned'
]

duplicates = orders.duplicated(subset=natural_key, keep='first')

# print("Dropped order_ids:")
# print(orders.loc[duplicates, 'order_id'].tolist())

orders_clean = orders.loc[~duplicates].copy()

#print("Shape:", orders_clean.shape)

"""Task 4 — Impute missing values"""

# Discount: fill missing values with 0
orders_clean['discount_pct'] = orders_clean['discount_pct'].fillna(0)

# Rating: calculate median before imputing
rating_median = orders_clean['rating'].median()
#print("Rating median:", rating_median)

# Fill missing ratings with median
orders_clean['rating'] = orders_clean['rating'].fillna(rating_median)
# Verify
#print(orders_clean[['discount_pct', 'rating']].isnull().sum())

"""Task 5 — Merge and reconcile against Part 1"""

# Merge orders with products
merged = orders_clean.merge(
    products[['product_id', 'price']],
    on='product_id',
    how='left'
)

# Merge with customers
merged = merged.merge(
    customers[['customer_id']],
    on='customer_id',
    how='left'
)

# Calculate order value
merged['order_value'] = (
    merged['quantity'] *
    merged['price'] *
    (1 - merged['discount_pct'] / 100)
)

#print("Cleaned order value:", round(merged['order_value'].sum(), 2))

dropped_orders = orders[duplicates].copy()

dropped_orders = dropped_orders.merge(
    products[['product_id', 'price']],
    on='product_id',
    how='left'
)

dropped_orders['order_value'] = (
    dropped_orders['quantity'] *
    dropped_orders['price'] *
    (1 - dropped_orders['discount_pct'].fillna(0) / 100)
)

#print("Dropped duplicates order_value:",
      round(dropped_orders['order_value'].sum(), 2))

#print("""
Reconciliation: The cleaned total order value is ₹97,358.30, which is ₹2,501.90 lower
than the Part 1 raw total of ₹99,860.20. This exact difference is attributable to the
5 duplicate rows (O0176–O0180) removed in Task 3, whose combined order value is
₹2,501.90. The discount and rating imputation in Task 4 does not change the order_value
total because discount values were missing and treated as 0%, while rating is not used
in the order_value calculation.
""")

"""Task 6 — IQR outlier detection on quantity"""

# Calculate IQR
Q1 = merged['quantity'].quantile(0.25)
Q3 = merged['quantity'].quantile(0.75)
IQR = Q3 - Q1

lower = Q1 - 1.5 * IQR
upper = Q3 + 1.5 * IQR

print("Q1:", Q1)
print("Q3:", Q3)
print("IQR:", IQR)
print("Lower:", lower)
print("Upper:", upper)

# Flag outliers — DO NOT DROP
merged['is_outlier'] = (
    (merged['quantity'] < lower) |
    (merged['quantity'] > upper)
)

# Show outlier rows
outliers = merged[merged['is_outlier']]

# print("\nOutlier rows:")
# print(outliers[['order_id', 'quantity', 'is_outlier']])
# print("\nNumber of outliers:", outliers.shape[0])

"""Task 7 — Hypothesis: does COD have a higher return rate?"""

# Task 7 — Hypothesis Test

#print("Hypothesis: COD has a higher return rate than other payment methods.")

return_rate = (
    merged.groupby('payment_method')['returned']
    .agg(['count', 'mean'])
)

return_rate['return_rate_pct'] = (return_rate['mean'] * 100).round(1)

# print("Return rate by payment method:")
# print(return_rate[['count', 'return_rate_pct']])

# print("\nHypothesis: Confirmed")

"""Task 8 — Multi-level segmentation"""

merged = merged.drop(columns=['city_tier'], errors='ignore')

merged = merged.merge(
    customers[['customer_id', 'city_tier']],
    on='customer_id',
    how='left'
)


segment = (
    merged.groupby(['payment_method', 'city_tier'])['returned']
    .agg(['count', 'mean'])
)

segment['return_rate_pct'] = (segment['mean'] * 100).round(1)

# print("Return rate by Payment Method and City Tier:")
# print(segment[['count', 'return_rate_pct']])

# print("\nHighest-risk segment:")
# print("COD + Tier-2 cities = 54.5% return rate")

# print("\nCOD segmentation:")
# print("Tier-1: 32 orders → 37.5% return rate")
# print("Tier-2: 22 orders → 54.5% return rate")

"""Task 9 — Correlation analysis"""

cols = ['rating', 'returned', 'discount_pct', 'quantity']

corr = merged[cols].corr()

# print("Correlation Matrix:")
# print(corr.round(2))

# print("\nCorrelation Strength Classification:")
# print("rating vs returned: Negligible")
# print("rating vs discount_pct: Negligible")
# print("rating vs quantity: Negligible")
# print("returned vs discount_pct: Negligible")
# print("returned vs quantity: Negligible")
# print("discount_pct vs quantity: Negligible")

# print("\nHypothesis: Higher discounts reduce returns")
# print("discount_pct vs returned correlation:", round(corr.loc['discount_pct', 'returned'], 2))
# print("Hypothesis: Busted")

"""Task 10 — Outlier-corrected time series"""

# Convert order_date to datetime
merged['order_date'] = pd.to_datetime(merged['order_date'])

# Extract year-month
merged['year_month'] = merged['order_date'].dt.to_period('M')

# 1. Monthly order value including outliers
monthly_with_outliers = (
    merged.groupby('year_month')['order_value']
    .sum()
    .round(2)
)

# print("Monthly order value INCLUDING outliers:")
# print(monthly_with_outliers)

# 2. Monthly order value excluding outliers
monthly_without_outliers = (
    merged[~merged['is_outlier']]
    .groupby('year_month')['order_value']
    .sum()
    .round(2)
)

# print("\nMonthly order value EXCLUDING outliers:")
# print(monthly_without_outliers)

# Explanation
#print("""
Reconciliation:
January's apparent lead is an artifact of the two bulk orders that landed
in January: O0011 on 2026-01-28 and O0098 on 2026-01-10. Once these two
outlier orders are excluded, March becomes the genuine peak month.
This demonstrates why the Task 6 outlier flag was created before Task 10.
""")
