"""
Extract Module
--------------
Handles data extraction from various sources (CSV files, APIs).
Generates sample e-commerce data for demonstration purposes.

In a production environment, this module would:
- Connect to source databases (PostgreSQL, MySQL, etc.)
- Fetch data from REST APIs (Shopify, Stripe, etc.)
- Read from cloud storage (S3, GCS, Azure Blob)
- Handle incremental extractions with watermarks
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import random

# ============================================
# Configuration
# ============================================

# Seed for reproducibility - ensures same data is generated each run
# Remove in production for real random data
np.random.seed(42)
random.seed(42)


# ============================================
# Data Generation Functions
# ============================================

def generate_customers(n_customers: int = 1000) -> pd.DataFrame:
    """
    Generate synthetic customer data.

    Simulates customer records that would typically come from:
    - CRM systems (Salesforce, HubSpot)
    - User registration databases
    - Marketing platforms

    Args:
        n_customers: Number of customers to generate

    Returns:
        DataFrame with customer information including:
        - customer_id: Unique identifier
        - first_name: Customer name
        - email: Contact email
        - region: Geographic region
        - country: Country code
        - signup_date: Account creation date
        - customer_segment: Business classification (Premium/Standard/Basic)
    """
    # Define possible values for categorical fields
    regions = ['North', 'South', 'East', 'West', 'Central']
    countries = ['USA', 'Canada', 'UK', 'Germany', 'France', 'Australia']

    # Generate customer DataFrame with synthetic data
    customers = pd.DataFrame({
        # Create unique IDs with consistent formatting (CUST_00001)
        'customer_id': [f'CUST_{i:05d}' for i in range(1, n_customers + 1)],
        'first_name': [f'Customer_{i}' for i in range(1, n_customers + 1)],
        'email': [f'customer_{i}@email.com' for i in range(1, n_customers + 1)],
        # Randomly assign regions and countries
        'region': np.random.choice(regions, n_customers),
        'country': np.random.choice(countries, n_customers),
        # Generate signup dates spread over 2 years (730 days)
        'signup_date': pd.to_datetime('2022-01-01') + pd.to_timedelta(
            np.random.randint(0, 730, n_customers), unit='D'
        ),
        # Weighted distribution: 20% Premium, 50% Standard, 30% Basic
        # This reflects typical customer pyramid distribution
        'customer_segment': np.random.choice(
            ['Premium', 'Standard', 'Basic'],
            n_customers,
            p=[0.2, 0.5, 0.3]
        )
    })

    return customers


def generate_products(n_products: int = 200) -> pd.DataFrame:
    """
    Generate synthetic product catalog.

    Simulates product data that would typically come from:
    - ERP systems (SAP, Oracle)
    - Product Information Management (PIM) systems
    - E-commerce platforms (Shopify, Magento)

    Args:
        n_products: Number of products to generate

    Returns:
        DataFrame with product information including pricing and categorization
    """
    # Define product hierarchy: categories and their subcategories
    categories = {
        'Electronics': ['Laptop', 'Phone', 'Tablet', 'Headphones', 'Camera'],
        'Clothing': ['Shirt', 'Pants', 'Jacket', 'Shoes', 'Accessories'],
        'Home & Garden': ['Furniture', 'Decor', 'Kitchen', 'Outdoor', 'Lighting'],
        'Sports': ['Fitness', 'Outdoor Gear', 'Team Sports', 'Water Sports', 'Cycling'],
        'Books': ['Fiction', 'Non-Fiction', 'Educational', 'Comics', 'Magazines']
    }

    products = []
    product_id = 1

    # Generate products for each category
    for category, subcategories in categories.items():
        # Distribute products evenly across categories
        n_cat_products = n_products // len(categories)

        for _ in range(n_cat_products):
            subcategory = random.choice(subcategories)

            # Define realistic price ranges by category
            # Electronics are typically higher priced, Books are lower
            base_prices = {
                'Electronics': (50, 2000),
                'Clothing': (20, 300),
                'Home & Garden': (30, 500),
                'Sports': (25, 400),
                'Books': (10, 100)
            }
            price_range = base_prices[category]

            products.append({
                'product_id': f'PROD_{product_id:05d}',
                'product_name': f'{subcategory} Item {product_id}',
                'category': category,
                'subcategory': subcategory,
                'unit_price': round(random.uniform(*price_range), 2),
                'cost_price': None,  # Will be calculated below
                'supplier_id': f'SUP_{random.randint(1, 20):03d}'
            })
            product_id += 1

    df = pd.DataFrame(products)

    # Calculate cost price as 40-70% of unit price (realistic margin range)
    # This allows for 30-60% gross margin which is typical for retail
    df['cost_price'] = (df['unit_price'] * np.random.uniform(0.4, 0.7, len(df))).round(2)

    return df


def generate_orders(
    customers: pd.DataFrame,
    products: pd.DataFrame,
    n_orders: int = 10000
) -> pd.DataFrame:
    """
    Generate synthetic order transactions.

    Simulates transactional data that would typically come from:
    - Point of Sale (POS) systems
    - E-commerce order management systems
    - Payment processors (Stripe, PayPal)

    Args:
        customers: Customer DataFrame for foreign key references
        products: Product DataFrame for foreign key references
        n_orders: Number of orders to generate

    Returns:
        DataFrame with order transactions including amounts and status
    """
    # Define date range for orders (2 years of data)
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2024, 12, 31)
    date_range = (end_date - start_date).days

    orders = []

    for i in range(1, n_orders + 1):
        # Randomly select a customer and product for each order
        customer = customers.sample(1).iloc[0]
        product = products.sample(1).iloc[0]

        # Generate random order date within the range
        day_offset = random.randint(0, date_range)
        order_date = start_date + timedelta(days=day_offset)

        # Simulate seasonal variation: Q4 (Nov-Dec) has higher sales
        # This reflects real-world holiday shopping patterns
        if order_date.month in [11, 12]:
            if random.random() > 0.3:  # 70% chance to keep Q4 orders
                pass

        # Generate quantity with realistic distribution
        # Most orders are for 1 item, fewer for multiple items
        quantity = np.random.choice([1, 2, 3, 4, 5], p=[0.5, 0.25, 0.15, 0.07, 0.03])
        unit_price = product['unit_price']

        # Apply random discounts (60% no discount, 40% some discount)
        discount_pct = np.random.choice([0, 0.05, 0.10, 0.15, 0.20], p=[0.6, 0.15, 0.12, 0.08, 0.05])

        # Calculate total after discount
        total_amount = round(quantity * unit_price * (1 - discount_pct), 2)

        orders.append({
            'order_id': f'ORD_{i:07d}',
            'customer_id': customer['customer_id'],
            'product_id': product['product_id'],
            'order_date': order_date,
            'quantity': quantity,
            'unit_price': unit_price,
            'discount_pct': discount_pct,
            'total_amount': total_amount,
            # Order status distribution: 75% completed, 5% cancelled
            'order_status': np.random.choice(
                ['Completed', 'Shipped', 'Processing', 'Cancelled'],
                p=[0.75, 0.15, 0.05, 0.05]
            ),
            # Payment method distribution reflects typical e-commerce
            'payment_method': np.random.choice(
                ['Credit Card', 'PayPal', 'Debit Card', 'Bank Transfer'],
                p=[0.45, 0.30, 0.15, 0.10]
            )
        })

    return pd.DataFrame(orders)


# ============================================
# Main Extraction Function
# ============================================

def extract_to_csv(output_dir: str = 'data/raw') -> dict:
    """
    Generate all datasets and save to CSV files.

    This is the main entry point for the Extract phase of ETL.
    In production, this would be replaced with actual data source connections.

    Args:
        output_dir: Directory to save CSV files

    Returns:
        Dictionary with paths to generated files
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    print("Extracting data...")

    # Generate datasets in dependency order
    # Customers and Products are independent
    # Orders depend on both (foreign key relationships)
    print("  - Generating customers...")
    customers = generate_customers(1000)

    print("  - Generating products...")
    products = generate_products(200)

    print("  - Generating orders...")
    orders = generate_orders(customers, products, 10000)

    # Save to CSV files (simulating data lake landing zone)
    paths = {}

    # Save customers
    customers_path = os.path.join(output_dir, 'customers.csv')
    customers.to_csv(customers_path, index=False)
    paths['customers'] = customers_path
    print(f"  - Saved {len(customers)} customers to {customers_path}")

    # Save products
    products_path = os.path.join(output_dir, 'products.csv')
    products.to_csv(products_path, index=False)
    paths['products'] = products_path
    print(f"  - Saved {len(products)} products to {products_path}")

    # Save orders
    orders_path = os.path.join(output_dir, 'orders.csv')
    orders.to_csv(orders_path, index=False)
    paths['orders'] = orders_path
    print(f"  - Saved {len(orders)} orders to {orders_path}")

    print("Extraction complete!")
    return paths


# ============================================
# Script Entry Point
# ============================================

if __name__ == '__main__':
    # When run directly, extract data to default location
    extract_to_csv()
