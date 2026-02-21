import pandas as pd
import os

# Path setup
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data")

# Load data
orders = pd.read_csv(os.path.join(DATA_PATH, "olist_orders_dataset.csv"))
order_items = pd.read_csv(os.path.join(DATA_PATH, "olist_order_items_dataset.csv"))
payments = pd.read_csv(os.path.join(DATA_PATH, "olist_order_payments_dataset.csv"))

# Convert date column
orders["order_purchase_timestamp"] = pd.to_datetime(
    orders["order_purchase_timestamp"]
)

# Merge orders + order_items
fact_orders = orders.merge(order_items, on="order_id", how="inner")

# Merge payments
fact_orders = fact_orders.merge(payments, on="order_id", how="left")

# Select important columns
fact_orders = fact_orders[
    [
        "order_id",
        "customer_id",
        "product_id",
        "seller_id",
        "order_purchase_timestamp",
        "price",
        "freight_value",
        "payment_value"
    ]
]

print("Final fact_orders shape:", fact_orders.shape)
print(fact_orders.head())

# Save transformed file
output_path = os.path.join(BASE_DIR, "data", "fact_orders.csv")
fact_orders.to_csv(output_path, index=False)

print("fact_orders.csv created successfully!")

# Remove rows where payment_value is null
fact_orders = fact_orders.dropna(subset=["payment_value"])

# Remove duplicate rows
fact_orders = fact_orders.drop_duplicates()

fact_orders["order_purchase_timestamp"] = pd.to_datetime(
    fact_orders["order_purchase_timestamp"]
)

fact_orders["price"] = fact_orders["price"].astype(float)
fact_orders["freight_value"] = fact_orders["freight_value"].astype(float)
fact_orders["payment_value"] = fact_orders["payment_value"].astype(float)

fact_orders["order_date"] = fact_orders["order_purchase_timestamp"].dt.date
fact_orders["order_year"] = fact_orders["order_purchase_timestamp"].dt.year
fact_orders["order_month"] = fact_orders["order_purchase_timestamp"].dt.month
fact_orders["order_day"] = fact_orders["order_purchase_timestamp"].dt.day

# Total order value
fact_orders["total_value"] = fact_orders["price"] + fact_orders["freight_value"]

print("Null values:")
print(fact_orders.isnull().sum())

print("Duplicate rows:", fact_orders.duplicated().sum())

print("Final shape:", fact_orders.shape)

fact_orders.to_csv(
    os.path.join(DATA_PATH, "fact_orders_clean.csv"),
    index=False
)