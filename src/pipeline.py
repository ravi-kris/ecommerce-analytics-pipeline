"""
Pipeline Orchestrator
---------------------
Main ETL pipeline that coordinates extraction, transformation, and loading.
Can be scheduled to run periodically.

This module serves as the entry point for the entire data pipeline.
In production, this would be orchestrated by tools like:
- Apache Airflow (DAGs)
- Prefect (Flows)
- Dagster (Pipelines)
- AWS Step Functions
- Azure Data Factory

Key concepts demonstrated:
- Pipeline orchestration
- Modular ETL design
- Configuration management
- Logging and monitoring
"""

import os
import sys
from datetime import datetime

# Add src directory to Python path for imports
# This allows running the script from any directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import ETL modules
from extract import extract_to_csv
from transform import run_transformations
from load import load_all_data
from analytics import run_all_analytics
from visualize import generate_dashboard


# ============================================
# Pipeline Orchestrator
# ============================================

def run_pipeline(
    generate_data: bool = True,
    run_analytics: bool = True,
    create_dashboard: bool = True
) -> None:
    """
    Run the complete ETL pipeline.

    This function orchestrates all phases of the data pipeline:
    1. EXTRACT: Generate/fetch source data
    2. TRANSFORM: Clean, validate, and transform data
    3. LOAD: Load into the data warehouse
    4. ANALYZE: Run analytics queries
    5. VISUALIZE: Generate dashboard

    Args:
        generate_data: Whether to generate new sample data
            Set to False to reprocess existing data
        run_analytics: Whether to run analytics queries
            Can skip for faster pipeline runs
        create_dashboard: Whether to generate the dashboard
            Can skip if only updating data
    """
    # ---- Pipeline Header ----
    print("=" * 60)
    print("E-commerce Analytics Pipeline")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # ---- Configure Paths ----
    # Use absolute paths for reliability
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_data_dir = os.path.join(base_dir, 'data', 'raw')
    processed_data_dir = os.path.join(base_dir, 'data', 'processed')
    db_path = os.path.join(base_dir, 'data', 'warehouse.db')
    reports_dir = os.path.join(base_dir, 'reports')

    # ============================================
    # STEP 1: EXTRACT
    # ============================================
    # In production: Connect to source systems, APIs, files
    # Here: Generate synthetic data for demonstration
    print("\n" + "=" * 60)
    print("STEP 1: EXTRACT")
    print("=" * 60)
    if generate_data:
        extract_to_csv(raw_data_dir)
    else:
        print("Skipping data generation (using existing data)")

    # ============================================
    # STEP 2: TRANSFORM
    # ============================================
    # Clean, validate, and transform raw data
    # Apply business logic and create dimensional model
    print("\n" + "=" * 60)
    print("STEP 2: TRANSFORM")
    print("=" * 60)
    datasets = run_transformations(raw_data_dir, processed_data_dir)

    # ============================================
    # STEP 3: LOAD
    # ============================================
    # Load transformed data into the data warehouse
    # Create schema, indexes, and relationships
    print("\n" + "=" * 60)
    print("STEP 3: LOAD")
    print("=" * 60)
    load_all_data(datasets, processed_data_dir, db_path)

    # ============================================
    # STEP 4: ANALYTICS (Optional)
    # ============================================
    # Run business intelligence queries
    # Generate insights from the data
    if run_analytics:
        print("\n" + "=" * 60)
        print("STEP 4: ANALYTICS")
        print("=" * 60)
        run_all_analytics(db_path)

    # ============================================
    # STEP 5: VISUALIZATION (Optional)
    # ============================================
    # Generate interactive dashboard
    # Create HTML report with embedded charts
    if create_dashboard:
        print("\n" + "=" * 60)
        print("STEP 5: VISUALIZATION")
        print("=" * 60)
        report_path = generate_dashboard(db_path, reports_dir)
        print(f"\nOpen the dashboard: file://{os.path.abspath(report_path)}")

    # ---- Pipeline Footer ----
    print("\n" + "=" * 60)
    print("Pipeline Complete!")
    print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)


# ============================================
# Script Entry Point
# ============================================

if __name__ == '__main__':
    # Run full pipeline when executed directly
    run_pipeline()
