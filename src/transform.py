"""
Transform Module
----------------
Handles data cleaning, validation, and transformation.
Implements data quality checks and business logic transformations.

This module demonstrates key data engineering concepts:
- Data quality validation (nulls, duplicates, referential integrity)
- Data standardization (text normalization, date parsing)
- Feature engineering (derived columns, calculated fields)
- Dimensional modeling (creating dimension and fact tables)
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os
from typing import Tuple, Dict, Any


# ============================================
# Data Quality Framework
# ============================================

class DataQualityChecker:
    """
    Performs data quality validations and generates reports.

    This class implements common data quality checks that would be
    performed in production pipelines using tools like:
    - Great Expectations
    - dbt tests
    - Apache Griffin
    """

    def __init__(self):
        # Store all identified issues for reporting
        self.issues = []

    def check_nulls(self, df: pd.DataFrame, columns: list, table_name: str) -> None:
        """
        Check for null values in specified columns.

        Null checks are critical for:
        - Primary key columns (should never be null)
        - Required business fields
        - Foreign key references
        """
        for col in columns:
            null_count = df[col].isnull().sum()
            if null_count > 0:
                self.issues.append({
                    'table': table_name,
                    'column': col,
                    'issue': 'Null values',
                    'count': null_count,
                    'severity': 'HIGH'
                })

    def check_duplicates(self, df: pd.DataFrame, key_columns: list, table_name: str) -> None:
        """
        Check for duplicate records based on key columns.

        Duplicate detection prevents:
        - Inflated metrics (double-counting)
        - Primary key violations
        - Data inconsistencies
        """
        dup_count = df.duplicated(subset=key_columns).sum()
        if dup_count > 0:
            self.issues.append({
                'table': table_name,
                'column': ', '.join(key_columns),
                'issue': 'Duplicate records',
                'count': dup_count,
                'severity': 'HIGH'
            })

    def check_negative_values(self, df: pd.DataFrame, columns: list, table_name: str) -> None:
        """
        Check for negative values in numeric columns.

        Important for columns that should always be positive:
        - Prices, quantities, amounts
        - Counts and totals
        """
        for col in columns:
            neg_count = (df[col] < 0).sum()
            if neg_count > 0:
                self.issues.append({
                    'table': table_name,
                    'column': col,
                    'issue': 'Negative values',
                    'count': neg_count,
                    'severity': 'MEDIUM'
                })

    def check_date_range(self, df: pd.DataFrame, date_col: str,
                         min_date: datetime, max_date: datetime, table_name: str) -> None:
        """
        Check if dates fall within expected range.

        Catches issues like:
        - Future dates that shouldn't exist yet
        - Very old dates indicating data corruption
        - Timezone conversion errors
        """
        out_of_range = ((df[date_col] < min_date) | (df[date_col] > max_date)).sum()
        if out_of_range > 0:
            self.issues.append({
                'table': table_name,
                'column': date_col,
                'issue': f'Dates outside range {min_date.date()} to {max_date.date()}',
                'count': out_of_range,
                'severity': 'MEDIUM'
            })

    def get_report(self) -> pd.DataFrame:
        """Generate data quality report as a DataFrame."""
        if not self.issues:
            print("No data quality issues found!")
            return pd.DataFrame()
        return pd.DataFrame(self.issues)


# ============================================
# Transformation Functions
# ============================================

def transform_customers(df: pd.DataFrame, checker: DataQualityChecker) -> pd.DataFrame:
    """
    Transform and clean customer data.

    Transformations applied:
    1. Data quality validation
    2. Text standardization (case normalization)
    3. Date parsing
    4. Feature engineering (days since signup)
    5. Deduplication

    Args:
        df: Raw customer DataFrame
        checker: DataQualityChecker instance

    Returns:
        Cleaned customer DataFrame ready for dimensional modeling
    """
    print("  - Transforming customers...")

    # Create a copy to avoid modifying original (important for debugging)
    df = df.copy()

    # ---- Data Quality Checks ----
    # Validate critical columns before transformation
    checker.check_nulls(df, ['customer_id', 'email'], 'customers')
    checker.check_duplicates(df, ['customer_id'], 'customers')

    # ---- Text Standardization ----
    # Normalize text fields for consistent querying and grouping
    df['region'] = df['region'].str.strip().str.title()      # "  north " -> "North"
    df['country'] = df['country'].str.strip().str.upper()    # "usa" -> "USA"
    df['customer_segment'] = df['customer_segment'].str.strip().str.title()

    # ---- Date Processing ----
    # Ensure date column is proper datetime type
    df['signup_date'] = pd.to_datetime(df['signup_date'])

    # ---- Feature Engineering ----
    # Add derived columns useful for analytics
    df['days_since_signup'] = (datetime.now() - df['signup_date']).dt.days
    df['signup_year'] = df['signup_date'].dt.year
    df['signup_month'] = df['signup_date'].dt.month

    # ---- Deduplication ----
    # Keep first occurrence in case of duplicates
    df = df.drop_duplicates(subset=['customer_id'], keep='first')

    return df


def transform_products(df: pd.DataFrame, checker: DataQualityChecker) -> pd.DataFrame:
    """
    Transform and clean product data.

    Transformations applied:
    1. Data quality validation
    2. Text standardization
    3. Calculated metrics (profit margin)
    4. Categorization (price tiers)
    5. Deduplication

    Args:
        df: Raw product DataFrame
        checker: DataQualityChecker instance

    Returns:
        Cleaned product DataFrame with derived metrics
    """
    print("  - Transforming products...")

    df = df.copy()

    # ---- Data Quality Checks ----
    checker.check_nulls(df, ['product_id', 'unit_price'], 'products')
    checker.check_duplicates(df, ['product_id'], 'products')
    checker.check_negative_values(df, ['unit_price', 'cost_price'], 'products')

    # ---- Text Standardization ----
    df['category'] = df['category'].str.strip().str.title()
    df['subcategory'] = df['subcategory'].str.strip().str.title()

    # ---- Calculated Metrics ----
    # Profit margin = (Revenue - Cost) / Revenue * 100
    df['profit_margin'] = ((df['unit_price'] - df['cost_price']) / df['unit_price'] * 100).round(2)

    # ---- Price Tier Categorization ----
    # Bin products into price tiers for easier analysis
    df['price_tier'] = pd.cut(
        df['unit_price'],
        bins=[0, 50, 200, 500, float('inf')],
        labels=['Budget', 'Mid-Range', 'Premium', 'Luxury']
    )

    # ---- Deduplication ----
    df = df.drop_duplicates(subset=['product_id'], keep='first')

    return df


def transform_orders(
    df: pd.DataFrame,
    customers: pd.DataFrame,
    products: pd.DataFrame,
    checker: DataQualityChecker
) -> pd.DataFrame:
    """
    Transform and clean order data (fact table).

    Transformations applied:
    1. Data quality validation
    2. Referential integrity checks
    3. Date parsing and time dimensions
    4. Calculated fields (gross amount, discount amount)
    5. Status standardization

    Args:
        df: Raw orders DataFrame
        customers: Cleaned customers DataFrame (for FK validation)
        products: Cleaned products DataFrame (for FK validation)
        checker: DataQualityChecker instance

    Returns:
        Cleaned orders DataFrame ready for the fact table
    """
    print("  - Transforming orders...")

    df = df.copy()

    # ---- Data Quality Checks ----
    checker.check_nulls(df, ['order_id', 'customer_id', 'product_id', 'total_amount'], 'orders')
    checker.check_duplicates(df, ['order_id'], 'orders')
    checker.check_negative_values(df, ['quantity', 'total_amount'], 'orders')

    # ---- Date Processing ----
    df['order_date'] = pd.to_datetime(df['order_date'])

    # Validate date range (no future orders, no very old orders)
    checker.check_date_range(
        df, 'order_date',
        datetime(2020, 1, 1), datetime.now(),
        'orders'
    )

    # ---- Referential Integrity ----
    # Ensure all foreign keys reference valid records
    valid_customers = set(customers['customer_id'])
    valid_products = set(products['product_id'])

    invalid_customers = ~df['customer_id'].isin(valid_customers)
    invalid_products = ~df['product_id'].isin(valid_products)

    # Log referential integrity issues
    if invalid_customers.sum() > 0:
        checker.issues.append({
            'table': 'orders',
            'column': 'customer_id',
            'issue': 'Invalid customer references',
            'count': invalid_customers.sum(),
            'severity': 'HIGH'
        })

    if invalid_products.sum() > 0:
        checker.issues.append({
            'table': 'orders',
            'column': 'product_id',
            'issue': 'Invalid product references',
            'count': invalid_products.sum(),
            'severity': 'HIGH'
        })

    # Filter out records with invalid foreign keys
    df = df[df['customer_id'].isin(valid_customers) & df['product_id'].isin(valid_products)]

    # ---- Time Dimension Attributes ----
    # Extract date parts for easier time-based analysis
    df['order_year'] = df['order_date'].dt.year
    df['order_month'] = df['order_date'].dt.month
    df['order_quarter'] = df['order_date'].dt.quarter
    df['order_day_of_week'] = df['order_date'].dt.dayofweek  # 0=Monday, 6=Sunday
    df['order_week'] = df['order_date'].dt.isocalendar().week
    df['is_weekend'] = df['order_day_of_week'].isin([5, 6])  # Saturday or Sunday

    # ---- Calculated Amount Fields ----
    # Gross amount before any discounts
    df['gross_amount'] = df['quantity'] * df['unit_price']
    # Total discount given on this order
    df['discount_amount'] = df['gross_amount'] - df['total_amount']

    # ---- Status Standardization ----
    df['order_status'] = df['order_status'].str.strip().str.title()

    # ---- Deduplication ----
    df = df.drop_duplicates(subset=['order_id'], keep='first')

    return df


def create_date_dimension(start_date: str = '2020-01-01', end_date: str = '2025-12-31') -> pd.DataFrame:
    """
    Create a date dimension table for time-based analysis.

    Date dimensions are essential in star schema design for:
    - Consistent date formatting across reports
    - Easy date-based filtering and grouping
    - Support for fiscal calendars
    - Holiday and special date flagging

    Args:
        start_date: Start date for the dimension
        end_date: End date for the dimension

    Returns:
        Date dimension DataFrame with various date attributes
    """
    print("  - Creating date dimension...")

    # Generate a date range
    dates = pd.date_range(start=start_date, end=end_date, freq='D')

    # Create date dimension with various useful attributes
    date_dim = pd.DataFrame({
        # Surrogate key in YYYYMMDD format (useful for partitioning)
        'date_key': dates.strftime('%Y%m%d').astype(int),
        'date': dates,
        # Year attributes
        'year': dates.year,
        'quarter': dates.quarter,
        'month': dates.month,
        'month_name': dates.strftime('%B'),  # Full month name
        # Week attributes
        'week': dates.isocalendar().week,
        'day_of_month': dates.day,
        'day_of_week': dates.dayofweek,
        'day_name': dates.strftime('%A'),    # Full day name
        # Useful flags for filtering
        'is_weekend': dates.dayofweek.isin([5, 6]),
        'is_month_start': dates.is_month_start,
        'is_month_end': dates.is_month_end,
        'is_quarter_start': dates.is_quarter_start,
        'is_quarter_end': dates.is_quarter_end
    })

    return date_dim


# ============================================
# Main Transformation Function
# ============================================

def run_transformations(input_dir: str = 'data/raw', output_dir: str = 'data/processed') -> Dict[str, pd.DataFrame]:
    """
    Run all transformations on extracted data.

    This is the main entry point for the Transform phase of ETL.
    It orchestrates all data cleaning, validation, and transformation steps.

    Args:
        input_dir: Directory containing raw CSV files
        output_dir: Directory to save processed files

    Returns:
        Dictionary of transformed DataFrames ready for loading
    """
    os.makedirs(output_dir, exist_ok=True)

    print("Transforming data...")

    # Initialize data quality checker to collect issues across all tables
    checker = DataQualityChecker()

    # ---- Load Raw Data ----
    customers_raw = pd.read_csv(os.path.join(input_dir, 'customers.csv'))
    products_raw = pd.read_csv(os.path.join(input_dir, 'products.csv'))
    orders_raw = pd.read_csv(os.path.join(input_dir, 'orders.csv'))

    # ---- Transform Data ----
    # Order matters: transform dimensions first, then facts
    customers = transform_customers(customers_raw, checker)
    products = transform_products(products_raw, checker)
    orders = transform_orders(orders_raw, customers, products, checker)
    date_dim = create_date_dimension()

    # ---- Generate Data Quality Report ----
    quality_report = checker.get_report()
    if not quality_report.empty:
        print("\nData Quality Issues Found:")
        print(quality_report.to_string(index=False))
        # Save report for review
        quality_report.to_csv(os.path.join(output_dir, 'data_quality_report.csv'), index=False)

    # ---- Save Transformed Data ----
    # Using dimensional modeling naming convention (dim_ for dimensions, fact_ for facts)
    datasets = {
        'dim_customers': customers,
        'dim_products': products,
        'dim_date': date_dim,
        'fact_orders': orders
    }

    for name, df in datasets.items():
        path = os.path.join(output_dir, f'{name}.csv')
        df.to_csv(path, index=False)
        print(f"  - Saved {len(df)} records to {path}")

    print("Transformation complete!")
    return datasets


# ============================================
# Script Entry Point
# ============================================

if __name__ == '__main__':
    run_transformations()
