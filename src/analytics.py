"""
Analytics Module
----------------
SQL-based analytics queries for business intelligence.
Generates insights from the data warehouse.

This module demonstrates key SQL analytics concepts:
- Aggregations and GROUP BY
- JOINs across dimension and fact tables
- Window functions (NTILE, ROW_NUMBER)
- Common Table Expressions (CTEs)
- Subqueries for complex calculations
"""

import pandas as pd
from sqlalchemy import create_engine, text
from typing import Dict, Any


# ============================================
# Database Connection
# ============================================

def get_engine(db_path: str = 'data/warehouse.db'):
    """Get SQLAlchemy engine for the data warehouse."""
    return create_engine(f'sqlite:///{db_path}')


def run_query(engine, query: str) -> pd.DataFrame:
    """
    Execute SQL query and return results as DataFrame.

    Args:
        engine: SQLAlchemy engine
        query: SQL query string

    Returns:
        Query results as pandas DataFrame
    """
    with engine.connect() as conn:
        return pd.read_sql(query, conn)


# ============================================
# Revenue Analytics
# ============================================

def get_total_revenue(engine) -> pd.DataFrame:
    """
    Get overall revenue metrics.

    Key KPIs calculated:
    - Total orders (excluding cancelled)
    - Unique customers
    - Total revenue
    - Average order value (AOV)
    - Total units sold
    - Total discounts given
    """
    query = """
    SELECT
        COUNT(DISTINCT order_id) as total_orders,
        COUNT(DISTINCT customer_id) as unique_customers,
        SUM(total_amount) as total_revenue,
        AVG(total_amount) as avg_order_value,
        SUM(quantity) as total_units_sold,
        SUM(discount_amount) as total_discounts
    FROM fact_orders
    WHERE order_status != 'Cancelled'  -- Exclude cancelled orders from revenue
    """
    return run_query(engine, query)


def get_revenue_by_month(engine) -> pd.DataFrame:
    """
    Get monthly revenue trends.

    Useful for:
    - Identifying seasonal patterns
    - Month-over-month growth analysis
    - Forecasting
    """
    query = """
    SELECT
        order_year,
        order_month,
        COUNT(DISTINCT order_id) as orders,
        COUNT(DISTINCT customer_id) as customers,
        SUM(total_amount) as revenue,
        AVG(total_amount) as avg_order_value
    FROM fact_orders
    WHERE order_status != 'Cancelled'
    GROUP BY order_year, order_month
    ORDER BY order_year, order_month
    """
    return run_query(engine, query)


def get_revenue_by_category(engine) -> pd.DataFrame:
    """
    Get revenue breakdown by product category.

    Demonstrates:
    - JOIN between fact and dimension tables
    - Subquery for percentage calculation
    """
    query = """
    SELECT
        p.category,
        COUNT(DISTINCT o.order_id) as orders,
        SUM(o.quantity) as units_sold,
        SUM(o.total_amount) as revenue,
        AVG(o.total_amount) as avg_order_value,
        -- Calculate percentage of total revenue using a subquery
        SUM(o.total_amount) * 100.0 / (
            SELECT SUM(total_amount)
            FROM fact_orders
            WHERE order_status != 'Cancelled'
        ) as revenue_pct
    FROM fact_orders o
    JOIN dim_products p ON o.product_id = p.product_id
    WHERE o.order_status != 'Cancelled'
    GROUP BY p.category
    ORDER BY revenue DESC
    """
    return run_query(engine, query)


# ============================================
# Customer Analytics
# ============================================

def get_customer_segments(engine) -> pd.DataFrame:
    """
    Get customer segment analysis.

    Analyzes performance by customer segment (Premium/Standard/Basic)
    to understand which segments drive the most value.
    """
    query = """
    SELECT
        c.customer_segment,
        COUNT(DISTINCT c.customer_id) as customers,
        COUNT(DISTINCT o.order_id) as orders,
        SUM(o.total_amount) as total_revenue,
        AVG(o.total_amount) as avg_order_value,
        -- Revenue per customer shows segment value
        SUM(o.total_amount) / COUNT(DISTINCT c.customer_id) as revenue_per_customer
    FROM dim_customers c
    LEFT JOIN fact_orders o ON c.customer_id = o.customer_id
        AND o.order_status != 'Cancelled'
    GROUP BY c.customer_segment
    ORDER BY total_revenue DESC
    """
    return run_query(engine, query)


def get_customer_rfm(engine) -> pd.DataFrame:
    """
    Calculate RFM (Recency, Frequency, Monetary) scores for customers.

    RFM Analysis is a customer segmentation technique:
    - Recency: How recently did the customer purchase?
    - Frequency: How often do they purchase?
    - Monetary: How much do they spend?

    Demonstrates:
    - Common Table Expressions (CTEs) for multi-step calculations
    - Window functions (NTILE) for scoring
    - CASE statements for segment classification
    """
    query = """
    -- Step 1: Calculate raw RFM metrics per customer
    WITH customer_metrics AS (
        SELECT
            customer_id,
            MAX(order_date) as last_order_date,
            COUNT(DISTINCT order_id) as frequency,
            SUM(total_amount) as monetary
        FROM fact_orders
        WHERE order_status != 'Cancelled'
        GROUP BY customer_id
    ),
    -- Step 2: Convert metrics to 1-5 scores using NTILE
    rfm_scores AS (
        SELECT
            customer_id,
            julianday('now') - julianday(last_order_date) as recency_days,
            frequency,
            monetary,
            -- NTILE(5) divides customers into 5 equal groups
            -- Lower recency (more recent) = higher score
            NTILE(5) OVER (ORDER BY julianday('now') - julianday(last_order_date) DESC) as r_score,
            -- Higher frequency = higher score
            NTILE(5) OVER (ORDER BY frequency) as f_score,
            -- Higher monetary = higher score
            NTILE(5) OVER (ORDER BY monetary) as m_score
        FROM customer_metrics
    )
    -- Step 3: Classify customers into segments based on scores
    SELECT
        customer_id,
        ROUND(recency_days, 0) as recency_days,
        frequency,
        ROUND(monetary, 2) as monetary,
        r_score,
        f_score,
        m_score,
        r_score + f_score + m_score as rfm_total,
        -- Business rules for customer classification
        CASE
            WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
            WHEN r_score >= 3 AND f_score >= 3 AND m_score >= 3 THEN 'Loyal Customers'
            WHEN r_score >= 4 AND f_score <= 2 THEN 'New Customers'
            WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk'
            WHEN r_score <= 2 AND f_score <= 2 THEN 'Lost'
            ELSE 'Regular'
        END as customer_segment
    FROM rfm_scores
    ORDER BY rfm_total DESC
    """
    return run_query(engine, query)


def get_top_customers(engine, limit: int = 10) -> pd.DataFrame:
    """
    Get top customers by revenue.

    Identifies highest-value customers for:
    - VIP programs
    - Retention focus
    - Upselling opportunities
    """
    query = f"""
    SELECT
        c.customer_id,
        c.first_name,
        c.customer_segment,
        c.region,
        COUNT(DISTINCT o.order_id) as total_orders,
        SUM(o.total_amount) as total_spent,
        AVG(o.total_amount) as avg_order_value,
        MIN(o.order_date) as first_order,
        MAX(o.order_date) as last_order
    FROM dim_customers c
    JOIN fact_orders o ON c.customer_id = o.customer_id
    WHERE o.order_status != 'Cancelled'
    GROUP BY c.customer_id, c.first_name, c.customer_segment, c.region
    ORDER BY total_spent DESC
    LIMIT {limit}
    """
    return run_query(engine, query)


# ============================================
# Product Analytics
# ============================================

def get_top_products(engine, limit: int = 10) -> pd.DataFrame:
    """
    Get top selling products.

    Identifies best performers for:
    - Inventory management
    - Marketing focus
    - Supplier negotiations
    """
    query = f"""
    SELECT
        p.product_id,
        p.product_name,
        p.category,
        p.subcategory,
        p.unit_price,
        p.profit_margin,
        COUNT(DISTINCT o.order_id) as orders,
        SUM(o.quantity) as units_sold,
        SUM(o.total_amount) as revenue
    FROM dim_products p
    JOIN fact_orders o ON p.product_id = o.product_id
    WHERE o.order_status != 'Cancelled'
    GROUP BY p.product_id, p.product_name, p.category, p.subcategory,
             p.unit_price, p.profit_margin
    ORDER BY revenue DESC
    LIMIT {limit}
    """
    return run_query(engine, query)


def get_category_performance(engine) -> pd.DataFrame:
    """
    Get detailed category performance metrics.

    Combines product and order data to show:
    - Category revenue contribution
    - Average profit margins
    - Order patterns
    """
    query = """
    SELECT
        p.category,
        COUNT(DISTINCT p.product_id) as products,
        COUNT(DISTINCT o.order_id) as orders,
        SUM(o.quantity) as units_sold,
        SUM(o.total_amount) as revenue,
        AVG(p.profit_margin) as avg_profit_margin,
        SUM(o.total_amount) / COUNT(DISTINCT o.order_id) as avg_order_value
    FROM dim_products p
    JOIN fact_orders o ON p.product_id = o.product_id
    WHERE o.order_status != 'Cancelled'
    GROUP BY p.category
    ORDER BY revenue DESC
    """
    return run_query(engine, query)


# ============================================
# Geographic Analytics
# ============================================

def get_revenue_by_region(engine) -> pd.DataFrame:
    """
    Get revenue breakdown by region.

    Geographic analysis for:
    - Regional marketing strategies
    - Expansion planning
    - Logistics optimization
    """
    query = """
    SELECT
        c.region,
        COUNT(DISTINCT c.customer_id) as customers,
        COUNT(DISTINCT o.order_id) as orders,
        SUM(o.total_amount) as revenue,
        AVG(o.total_amount) as avg_order_value,
        SUM(o.total_amount) / COUNT(DISTINCT c.customer_id) as revenue_per_customer
    FROM dim_customers c
    JOIN fact_orders o ON c.customer_id = o.customer_id
    WHERE o.order_status != 'Cancelled'
    GROUP BY c.region
    ORDER BY revenue DESC
    """
    return run_query(engine, query)


def get_revenue_by_country(engine) -> pd.DataFrame:
    """Get revenue breakdown by country."""
    query = """
    SELECT
        c.country,
        COUNT(DISTINCT c.customer_id) as customers,
        COUNT(DISTINCT o.order_id) as orders,
        SUM(o.total_amount) as revenue,
        AVG(o.total_amount) as avg_order_value
    FROM dim_customers c
    JOIN fact_orders o ON c.customer_id = o.customer_id
    WHERE o.order_status != 'Cancelled'
    GROUP BY c.country
    ORDER BY revenue DESC
    """
    return run_query(engine, query)


# ============================================
# Time-based Analytics
# ============================================

def get_daily_trends(engine) -> pd.DataFrame:
    """
    Get daily order trends.

    Time series data for:
    - Trend visualization
    - Anomaly detection
    - Forecasting models
    """
    query = """
    SELECT
        order_date,
        COUNT(DISTINCT order_id) as orders,
        SUM(total_amount) as revenue,
        COUNT(DISTINCT customer_id) as unique_customers
    FROM fact_orders
    WHERE order_status != 'Cancelled'
    GROUP BY order_date
    ORDER BY order_date
    """
    return run_query(engine, query)


def get_day_of_week_analysis(engine) -> pd.DataFrame:
    """
    Get performance by day of week.

    Useful for:
    - Staffing decisions
    - Promotion timing
    - Understanding customer behavior patterns
    """
    query = """
    SELECT
        order_day_of_week,
        -- Convert numeric day to readable name
        CASE order_day_of_week
            WHEN 0 THEN 'Monday'
            WHEN 1 THEN 'Tuesday'
            WHEN 2 THEN 'Wednesday'
            WHEN 3 THEN 'Thursday'
            WHEN 4 THEN 'Friday'
            WHEN 5 THEN 'Saturday'
            WHEN 6 THEN 'Sunday'
        END as day_name,
        COUNT(DISTINCT order_id) as orders,
        SUM(total_amount) as revenue,
        AVG(total_amount) as avg_order_value
    FROM fact_orders
    WHERE order_status != 'Cancelled'
    GROUP BY order_day_of_week
    ORDER BY order_day_of_week
    """
    return run_query(engine, query)


# ============================================
# Main Analytics Runner
# ============================================

def run_all_analytics(db_path: str = 'data/warehouse.db') -> Dict[str, pd.DataFrame]:
    """
    Run all analytics queries and return results.

    This function executes all analytics queries and prints
    formatted results to the console. Useful for quick data exploration.

    Args:
        db_path: Path to the SQLite database

    Returns:
        Dictionary of analytics results as DataFrames
    """
    print("Running analytics queries...")

    engine = get_engine(db_path)
    results = {}

    # ---- Revenue Analytics ----
    print("\n=== Revenue Analytics ===")

    results['total_revenue'] = get_total_revenue(engine)
    print("\nOverall Metrics:")
    print(results['total_revenue'].to_string(index=False))

    results['revenue_by_month'] = get_revenue_by_month(engine)
    print("\nMonthly Revenue (last 5 months):")
    print(results['revenue_by_month'].tail().to_string(index=False))

    results['revenue_by_category'] = get_revenue_by_category(engine)
    print("\nRevenue by Category:")
    print(results['revenue_by_category'].to_string(index=False))

    # ---- Customer Analytics ----
    print("\n=== Customer Analytics ===")

    results['customer_segments'] = get_customer_segments(engine)
    print("\nCustomer Segments:")
    print(results['customer_segments'].to_string(index=False))

    results['top_customers'] = get_top_customers(engine)
    print("\nTop 10 Customers:")
    print(results['top_customers'].to_string(index=False))

    results['customer_rfm'] = get_customer_rfm(engine)
    rfm_summary = results['customer_rfm'].groupby('customer_segment').size().reset_index(name='count')
    print("\nRFM Customer Segments:")
    print(rfm_summary.to_string(index=False))

    # ---- Product Analytics ----
    print("\n=== Product Analytics ===")

    results['top_products'] = get_top_products(engine)
    print("\nTop 10 Products:")
    print(results['top_products'][['product_name', 'category', 'units_sold', 'revenue']].to_string(index=False))

    # ---- Geographic Analytics ----
    print("\n=== Geographic Analytics ===")

    results['revenue_by_region'] = get_revenue_by_region(engine)
    print("\nRevenue by Region:")
    print(results['revenue_by_region'].to_string(index=False))

    # ---- Time Analytics ----
    print("\n=== Time-based Analytics ===")

    results['day_of_week'] = get_day_of_week_analysis(engine)
    print("\nPerformance by Day of Week:")
    print(results['day_of_week'].to_string(index=False))

    print("\nAnalytics complete!")
    return results


# ============================================
# Script Entry Point
# ============================================

if __name__ == '__main__':
    run_all_analytics()
