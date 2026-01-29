"""
Power BI Export Module
----------------------
Exports analytics data to formats compatible with Power BI.

Power BI can connect to:
- Excel files (.xlsx) - Best for small to medium datasets
- CSV files - Universal compatibility
- SQL databases - For live connections
- Azure services - For enterprise deployments

This module exports pre-aggregated analytics tables that can be
directly imported into Power BI for dashboard creation.

Usage:
    python src/export_powerbi.py

Output:
    Creates Excel files in the 'powerbi/' directory ready for import.
"""

import pandas as pd
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from analytics import (
    get_engine,
    get_total_revenue,
    get_revenue_by_month,
    get_revenue_by_category,
    get_customer_segments,
    get_top_products,
    get_revenue_by_region,
    get_revenue_by_country,
    get_day_of_week_analysis,
    get_customer_rfm,
    get_top_customers,
    get_daily_trends
)


def export_for_powerbi(db_path: str = None, output_dir: str = None) -> None:
    """
    Export all analytics data to Excel files for Power BI.

    Creates multiple Excel files organized by analytics domain:
    - revenue_analytics.xlsx: Revenue trends and breakdowns
    - customer_analytics.xlsx: Customer segments and RFM
    - product_analytics.xlsx: Product performance
    - geographic_analytics.xlsx: Regional analysis
    - time_analytics.xlsx: Time-based trends

    Args:
        db_path: Path to the SQLite database
        output_dir: Directory to save Excel files
    """
    # Set default paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    if db_path is None:
        db_path = os.path.join(base_dir, 'data', 'warehouse.db')

    if output_dir is None:
        output_dir = os.path.join(base_dir, 'powerbi')

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 60)
    print("Exporting Data for Power BI")
    print("=" * 60)

    # Get database connection
    engine = get_engine(db_path)

    # ============================================
    # Revenue Analytics Export
    # ============================================
    print("\nExporting Revenue Analytics...")

    revenue_file = os.path.join(output_dir, 'revenue_analytics.xlsx')
    with pd.ExcelWriter(revenue_file, engine='openpyxl') as writer:
        # Overall KPIs
        get_total_revenue(engine).to_excel(writer, sheet_name='KPI_Summary', index=False)
        print("  - KPI Summary")

        # Monthly trends
        get_revenue_by_month(engine).to_excel(writer, sheet_name='Monthly_Trends', index=False)
        print("  - Monthly Trends")

        # Category breakdown
        get_revenue_by_category(engine).to_excel(writer, sheet_name='By_Category', index=False)
        print("  - By Category")

    print(f"  Saved to: {revenue_file}")

    # ============================================
    # Customer Analytics Export
    # ============================================
    print("\nExporting Customer Analytics...")

    customer_file = os.path.join(output_dir, 'customer_analytics.xlsx')
    with pd.ExcelWriter(customer_file, engine='openpyxl') as writer:
        # Customer segments
        get_customer_segments(engine).to_excel(writer, sheet_name='Segments', index=False)
        print("  - Customer Segments")

        # RFM Analysis
        rfm_data = get_customer_rfm(engine)
        rfm_data.to_excel(writer, sheet_name='RFM_Detail', index=False)
        print("  - RFM Detail")

        # RFM Summary
        rfm_summary = rfm_data.groupby('customer_segment').agg({
            'customer_id': 'count',
            'monetary': 'sum',
            'frequency': 'mean',
            'recency_days': 'mean'
        }).reset_index()
        rfm_summary.columns = ['Segment', 'Customer_Count', 'Total_Revenue', 'Avg_Frequency', 'Avg_Recency_Days']
        rfm_summary.to_excel(writer, sheet_name='RFM_Summary', index=False)
        print("  - RFM Summary")

        # Top customers
        get_top_customers(engine, limit=100).to_excel(writer, sheet_name='Top_Customers', index=False)
        print("  - Top Customers")

    print(f"  Saved to: {customer_file}")

    # ============================================
    # Product Analytics Export
    # ============================================
    print("\nExporting Product Analytics...")

    product_file = os.path.join(output_dir, 'product_analytics.xlsx')
    with pd.ExcelWriter(product_file, engine='openpyxl') as writer:
        # Top products
        get_top_products(engine, limit=100).to_excel(writer, sheet_name='Top_Products', index=False)
        print("  - Top Products")

        # Category performance
        get_revenue_by_category(engine).to_excel(writer, sheet_name='Category_Performance', index=False)
        print("  - Category Performance")

    print(f"  Saved to: {product_file}")

    # ============================================
    # Geographic Analytics Export
    # ============================================
    print("\nExporting Geographic Analytics...")

    geo_file = os.path.join(output_dir, 'geographic_analytics.xlsx')
    with pd.ExcelWriter(geo_file, engine='openpyxl') as writer:
        # By region
        get_revenue_by_region(engine).to_excel(writer, sheet_name='By_Region', index=False)
        print("  - By Region")

        # By country
        get_revenue_by_country(engine).to_excel(writer, sheet_name='By_Country', index=False)
        print("  - By Country")

    print(f"  Saved to: {geo_file}")

    # ============================================
    # Time Analytics Export
    # ============================================
    print("\nExporting Time Analytics...")

    time_file = os.path.join(output_dir, 'time_analytics.xlsx')
    with pd.ExcelWriter(time_file, engine='openpyxl') as writer:
        # Daily trends
        get_daily_trends(engine).to_excel(writer, sheet_name='Daily_Trends', index=False)
        print("  - Daily Trends")

        # Day of week
        get_day_of_week_analysis(engine).to_excel(writer, sheet_name='Day_of_Week', index=False)
        print("  - Day of Week")

        # Monthly trends
        get_revenue_by_month(engine).to_excel(writer, sheet_name='Monthly_Trends', index=False)
        print("  - Monthly Trends")

    print(f"  Saved to: {time_file}")

    # ============================================
    # Summary
    # ============================================
    print("\n" + "=" * 60)
    print("Export Complete!")
    print("=" * 60)
    print(f"\nFiles exported to: {output_dir}/")
    print("""
Power BI Import Instructions:
1. Open Power BI Desktop
2. Click 'Get Data' > 'Excel'
3. Select the exported .xlsx files
4. Choose sheets to import
5. Create relationships between tables
6. Build your visualizations

Recommended Visualizations:
- KPI cards for revenue, orders, customers
- Line chart for monthly trends
- Bar chart for category comparison
- Map visual for geographic data
- Donut chart for customer segments
- Matrix for RFM analysis
""")


# ============================================
# Script Entry Point
# ============================================

if __name__ == '__main__':
    export_for_powerbi()
