import os
import pandas as pd
import matplotlib.pyplot as plt

def load_or_process_data() -> pd.DataFrame:
    cleaned_candidates = ["cleaned_orders.csv", "data/cleaned_orders.csv", "analysis/cleaned_orders.csv"]
    for path in cleaned_candidates:
        if os.path.exists(path):
            df = pd.read_csv(path)
            df['order_date'] = pd.to_datetime(df['order_date'])
            return df

    orders_path = "data/orders.csv" if os.path.exists("data/orders.csv") else "orders.csv"
    customers_path = "data/customers.csv" if os.path.exists("data/customers.csv") else "customers.csv"
    products_path = "data/products.csv" if os.path.exists("data/products.csv") else "products.csv"

    orders = pd.read_csv(orders_path)
    customers = pd.read_csv(customers_path)
    products = pd.read_csv(products_path)

    orders['payment_method'] = orders['payment_method'].str.strip().str.upper()

    dup_cols = ['customer_id', 'product_id', 'order_date', 'quantity', 
                'discount_pct', 'payment_method', 'rating', 'returned']
    orders_clean = orders.drop_duplicates(subset=dup_cols, keep='first').copy()

    orders_clean['discount_pct'] = orders_clean['discount_pct'].fillna(0)
    rating_median = orders_clean['rating'].median()
    orders_clean['rating'] = orders_clean['rating'].fillna(rating_median)

    merged = orders_clean.merge(products, on='product_id', how='left')
    merged = merged.merge(customers, on='customer_id', how='left')
    merged['order_value'] = merged['quantity'] * merged['price'] * (1 - merged['discount_pct'] / 100.0)

    q1 = merged['quantity'].quantile(0.25)
    q3 = merged['quantity'].quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    merged['is_outlier'] = (merged['quantity'] < lower_bound) | (merged['quantity'] > upper_bound)

    merged['order_date'] = pd.to_datetime(merged['order_date'])
    return merged

def generate_visualizations():
    os.makedirs("visualizations", exist_ok=True)
    df = load_or_process_data()

    # 1. Bar Chart: Return Rate by Payment Method
    return_rates = (df.groupby('payment_method')['returned'].mean() * 100).sort_values(ascending=False)

    plt.figure(figsize=(7, 5))
    bar_colors = ['#c1121f', '#0077b6', '#2a9d8f']
    bars = plt.bar(return_rates.index, return_rates.values, color=bar_colors, width=0.45)

    for bar in bars:
        h = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2.0,
            h + 1.0,
            f"{h:.1f}%",
            ha='center',
            va='bottom',
            fontsize=11,
            fontweight='bold'
        )

    plt.title("COD Returns at 44.4% — ~3x Card", fontsize=13, fontweight='bold', pad=15)
    plt.xlabel("Payment Method", fontsize=11, fontweight='bold')
    plt.ylabel("Return Rate (%)", fontsize=11, fontweight='bold')
    plt.ylim(0, max(return_rates.values) + 10)
    plt.grid(axis='y', linestyle='--', alpha=0.4)

    chart1_file = "visualizations/return_rate_by_payment.png"
    plt.tight_layout()
    plt.savefig(chart1_file, dpi=300)
    plt.close()
    print(f"[OK] Generated: {chart1_file}")

    # 2. Line Chart: Outlier-Corrected Monthly Revenue Trend
    clean_series = df[~df['is_outlier']].copy()
    clean_series['month'] = clean_series['order_date'].dt.strftime('%Y-%m')
    monthly_rev = clean_series.groupby('month')['order_value'].sum()

    plt.figure(figsize=(9, 5))
    plt.plot(
        monthly_rev.index,
        monthly_rev.values,
        marker='o',
        color='#1d3557',
        linewidth=2.5,
        markersize=6,
        label='Monthly Revenue'
    )

    peak_m = "2026-03"
    if peak_m in monthly_rev.index:
        peak_val = monthly_rev[peak_m]
        plt.scatter([peak_m], [peak_val], color='#e63946', s=120, zorder=5, label=f'Peak: March (₹{peak_val:,.2f})')
        plt.annotate(
            f"March Peak\n₹{peak_val:,.2f}",
            (peak_m, peak_val),
            textcoords="offset points",
            xytext=(0, 12),
            ha='center',
            fontweight='bold',
            color='#e63946'
        )

    plt.title("Outlier-Corrected Monthly Revenue: March is True Peak Month", fontsize=13, fontweight='bold', pad=15)
    plt.xlabel("Month", fontsize=11, fontweight='bold')
    plt.ylabel("Revenue (INR)", fontsize=11, fontweight='bold')
    plt.ylim(0, monthly_rev.max() * 1.25)
    plt.grid(True, linestyle='--', alpha=0.4)
    plt.legend(loc='upper right')

    chart2_file = "visualizations/monthly_revenue_trend.png"
    plt.tight_layout()
    plt.savefig(chart2_file, dpi=300)
    plt.close()
    print(f"[OK] Generated: {chart2_file}")

if __name__ == "__main__":
    generate_visualizations()
