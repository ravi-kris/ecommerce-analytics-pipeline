"""
Load Module
-----------
Handles loading transformed data into the SQLite data warehouse.
Creates schema and manages database operations.

In production, this module would load data into:
- Cloud data warehouses (Snowflake, BigQuery, Redshift)
- On-premise databases (PostgreSQL, SQL Server)
- Data lakes (Delta Lake, Apache Iceberg)

Key concepts demonstrated:
- Star schema design (dimension and fact tables)
- Database indexing for query performance
- Foreign key relationships for data integrity
"""

import pandas as pd
from sqlalchemy import create_engine, text
import os
from typing import Dict


# ============================================
# Database Schema Definition
# ============================================

# SQL statements to create the data warehouse schema
# Using star schema design pattern with dimension and fact tables
CREATE_SCHEMA_SQL = """
-- ============================================
-- DIMENSION TABLES
-- Dimension tables contain descriptive attributes
-- that provide context for fact table measurements
-- ============================================

-- Dimension: Customers
-- Contains customer attributes for segmentation and analysis
CREATE TABLE IF NOT EXISTS dim_customers (
    customer_id TEXT PRIMARY KEY,      -- Natural key from source system
    first_name TEXT,
    email TEXT,
    region TEXT,                       -- Geographic region for regional analysis
    country TEXT,
    signup_date DATE,
    customer_segment TEXT,             -- Business classification (Premium/Standard/Basic)
    days_since_signup INTEGER,         -- Derived: tenure in days
    signup_year INTEGER,               -- Derived: for year-over-year comparison
    signup_month INTEGER
);

-- Dimension: Products
-- Contains product catalog information
CREATE TABLE IF NOT EXISTS dim_products (
    product_id TEXT PRIMARY KEY,
    product_name TEXT,
    category TEXT,                     -- Top-level categorization
    subcategory TEXT,                  -- Detailed categorization
    unit_price REAL,
    cost_price REAL,                   -- For margin calculations
    supplier_id TEXT,
    profit_margin REAL,                -- Derived: (price - cost) / price * 100
    price_tier TEXT                    -- Derived: Budget/Mid-Range/Premium/Luxury
);

-- Dimension: Date
-- Standard date dimension for time-based analysis
-- Pre-calculated date attributes enable efficient time-based queries
CREATE TABLE IF NOT EXISTS dim_date (
    date_key INTEGER PRIMARY KEY,      -- Surrogate key in YYYYMMDD format
    date DATE,
    year INTEGER,
    quarter INTEGER,
    month INTEGER,
    month_name TEXT,
    week INTEGER,
    day_of_month INTEGER,
    day_of_week INTEGER,
    day_name TEXT,
    is_weekend BOOLEAN,
    is_month_start BOOLEAN,
    is_month_end BOOLEAN,
    is_quarter_start BOOLEAN,
    is_quarter_end BOOLEAN
);

-- ============================================
-- FACT TABLE
-- Fact tables contain measurable business events
-- with foreign keys to dimension tables
-- ============================================

-- Fact: Orders
-- Contains transactional order data with measurements
CREATE TABLE IF NOT EXISTS fact_orders (
    order_id TEXT PRIMARY KEY,         -- Natural key from source system
    customer_id TEXT,                  -- FK to dim_customers
    product_id TEXT,                   -- FK to dim_products
    order_date DATE,                   -- Can join to dim_date
    quantity INTEGER,                  -- Measure: units ordered
    unit_price REAL,                   -- Measure: price at time of order
    discount_pct REAL,                 -- Measure: discount percentage applied
    total_amount REAL,                 -- Measure: final amount after discount
    order_status TEXT,                 -- Status for filtering
    payment_method TEXT,
    order_year INTEGER,                -- Denormalized for query performance
    order_month INTEGER,
    order_quarter INTEGER,
    order_day_of_week INTEGER,
    order_week INTEGER,
    is_weekend BOOLEAN,
    gross_amount REAL,                 -- Measure: amount before discount
    discount_amount REAL,              -- Measure: discount value
    -- Foreign key constraints for referential integrity
    FOREIGN KEY (customer_id) REFERENCES dim_customers(customer_id),
    FOREIGN KEY (product_id) REFERENCES dim_products(product_id)
);

-- ============================================
-- INDEXES
-- Indexes improve query performance for common access patterns
-- ============================================

-- Indexes on foreign keys (common join columns)
CREATE INDEX IF NOT EXISTS idx_orders_customer ON fact_orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_product ON fact_orders(product_id);

-- Index on date for time-based queries
CREATE INDEX IF NOT EXISTS idx_orders_date ON fact_orders(order_date);

-- Index on status for filtering by order status
CREATE INDEX IF NOT EXISTS idx_orders_status ON fact_orders(order_status);

-- Indexes on dimension tables for common filter columns
CREATE INDEX IF NOT EXISTS idx_products_category ON dim_products(category);
CREATE INDEX IF NOT EXISTS idx_customers_segment ON dim_customers(customer_segment);
"""


# ============================================
# Database Functions
# ============================================

def create_database(db_path: str) -> object:
    """
    Create SQLite database and initialize schema.

    Creates the database file and executes DDL statements to create
    all tables and indexes defined in the schema.

    Args:
        db_path: Path to the SQLite database file

    Returns:
        SQLAlchemy engine object for database operations
    """
    # Ensure the data directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    # Create SQLAlchemy engine (connection pool manager)
    # SQLite is used for portability; in production, use cloud DW
    engine = create_engine(f'sqlite:///{db_path}')

    # Execute schema creation statements
    with engine.connect() as conn:
        # Split by semicolon and execute each statement
        for statement in CREATE_SCHEMA_SQL.split(';'):
            if statement.strip():
                conn.execute(text(statement))
        conn.commit()

    print(f"Database schema created at {db_path}")
    return engine


def load_dataframe(engine, df: pd.DataFrame, table_name: str, if_exists: str = 'replace') -> int:
    """
    Load a DataFrame into a database table.

    Uses pandas to_sql for efficient bulk loading.
    In production, consider using COPY commands or staging tables.

    Args:
        engine: SQLAlchemy engine
        df: DataFrame to load
        table_name: Target table name
        if_exists: Behavior if table exists
            - 'fail': Raise error
            - 'replace': Drop and recreate table
            - 'append': Insert new rows

    Returns:
        Number of records loaded
    """
    df.to_sql(table_name, engine, if_exists=if_exists, index=False)
    return len(df)


def load_all_data(
    datasets: Dict[str, pd.DataFrame] = None,
    input_dir: str = 'data/processed',
    db_path: str = 'data/warehouse.db'
) -> None:
    """
    Load all transformed data into the data warehouse.

    This is the main entry point for the Load phase of ETL.
    Handles loading in the correct order to satisfy foreign key constraints.

    Args:
        datasets: Dictionary of DataFrames (optional)
        input_dir: Directory containing processed CSV files
        db_path: Path to the SQLite database
    """
    print("Loading data into warehouse...")

    # Create database and schema
    engine = create_database(db_path)

    # Load from CSV if datasets not provided directly
    if datasets is None:
        datasets = {
            'dim_customers': pd.read_csv(os.path.join(input_dir, 'dim_customers.csv')),
            'dim_products': pd.read_csv(os.path.join(input_dir, 'dim_products.csv')),
            'dim_date': pd.read_csv(os.path.join(input_dir, 'dim_date.csv')),
            'fact_orders': pd.read_csv(os.path.join(input_dir, 'fact_orders.csv'))
        }

    # Load tables in correct order: dimensions first, then facts
    # This ensures foreign key references are valid
    load_order = ['dim_customers', 'dim_products', 'dim_date', 'fact_orders']

    for table_name in load_order:
        df = datasets[table_name]
        records = load_dataframe(engine, df, table_name)
        print(f"  - Loaded {records} records into {table_name}")

    # ---- Verify Data Load ----
    # Query row counts to confirm successful loading
    print("\nData Warehouse Summary:")
    with engine.connect() as conn:
        for table_name in load_order:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            count = result.scalar()
            print(f"  - {table_name}: {count:,} records")

    print("\nLoad complete!")
    return engine


def get_engine(db_path: str = 'data/warehouse.db'):
    """
    Get SQLAlchemy engine for the data warehouse.

    Utility function to get a database connection for queries.
    """
    return create_engine(f'sqlite:///{db_path}')


# ============================================
# Script Entry Point
# ============================================

if __name__ == '__main__':
    load_all_data()
