# E-commerce Sales Analytics Pipeline

A data engineering portfolio project demonstrating ETL pipelines, data modeling, SQL analytics, and multi-platform visualization.

## Project Overview

This project simulates a real-world data engineering workflow for an e-commerce company, including:

- **Data Ingestion**: Extract data from CSV files and APIs
- **Data Transformation**: Clean, validate, and transform raw data
- **Data Loading**: Load processed data into a SQLite data warehouse
- **Analytics**: SQL-based business intelligence queries
- **Visualization**: Multiple output formats for different use cases

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Sources   │────▶│   Extract   │────▶│  Transform  │────▶│    Load     │
│  (CSV/API)  │     │             │     │   & Clean   │     │  (SQLite)   │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                                                                  │
                                                                  ▼
                                                            ┌─────────────┐
                                                            │  Analytics  │
                                                            │    (SQL)    │
                                                            └─────────────┘
                                                                  │
                    ┌─────────────────────────────────────────────┼─────────────────────────────────────────────┐
                    ▼                                             ▼                                             ▼
            ┌─────────────┐                               ┌─────────────┐                               ┌─────────────┐
            │  Streamlit  │                               │ Matplotlib  │                               │  Power BI   │
            │  Web App    │                               │   Charts    │                               │   Export    │
            └─────────────┘                               └─────────────┘                               └─────────────┘
                    │                                             │                                             │
                    ▼                                             ▼                                             ▼
            ┌─────────────┐                               ┌─────────────┐                               ┌─────────────┐
            │ Interactive │                               │    PNG      │                               │    Excel    │
            │  Dashboard  │                               │   Reports   │                               │    Files    │
            └─────────────┘                               └─────────────┘                               └─────────────┘
```

## Tech Stack

- **Python 3.10+**
- **pandas** - Data manipulation and analysis
- **SQLAlchemy** - Database ORM and SQL toolkit
- **SQLite** - Lightweight data warehouse
- **Streamlit** - Interactive web applications
- **Plotly** - Interactive charts for dashboards
- **Matplotlib/Seaborn** - Static charts for reports
- **openpyxl** - Excel export for Power BI
- **Jinja2** - Report templating

## Project Structure

```
ecommerce-analytics-pipeline/
├── data/
│   ├── raw/                  # Raw source data
│   ├── processed/            # Cleaned data
│   └── warehouse.db          # SQLite database
├── src/
│   ├── extract.py            # Data extraction module
│   ├── transform.py          # Data transformation & cleaning
│   ├── load.py               # Database loading module
│   ├── analytics.py          # SQL analytics queries
│   ├── visualize.py          # HTML dashboard generation
│   ├── static_charts.py      # Matplotlib static charts
│   ├── export_powerbi.py     # Power BI Excel export
│   └── pipeline.py           # Main ETL orchestrator
├── reports/
│   ├── dashboard.html        # Interactive HTML report
│   └── charts/               # Static PNG charts
├── powerbi/                  # Excel files for Power BI
├── app.py                    # Streamlit web application
├── requirements.txt
└── README.md
```

## Data Model

### Dimension Tables
- **dim_customers** - Customer demographics (name, email, segment, region)
- **dim_products** - Product catalog (name, category, price)
- **dim_date** - Date dimension for time-based analysis

### Fact Tables
- **fact_orders** - Order transactions with metrics (quantity, revenue, discount)

## Key Metrics

- Total Revenue & Average Order Value
- Customer Lifetime Value (CLV)
- Product Performance Analysis
- Sales Trends (Daily/Monthly/Quarterly)
- Customer Segmentation (RFM Analysis)
- Geographic Sales Distribution

## Visualization Options

This project provides three visualization outputs for different use cases:

### 1. Streamlit Interactive Dashboard
Real-time interactive web application with filtering and exploration.

```bash
streamlit run app.py
```

**Features:**
- KPI metrics display
- Interactive Plotly charts
- Filter by category, region, time
- Multiple dashboard pages (Overview, Revenue, Customer, Product)

### 2. Static Charts (Matplotlib)
High-quality PNG charts for reports, presentations, and documentation.

```bash
python src/static_charts.py
```

**Output charts:**
- `revenue_trend.png` - Monthly revenue line chart
- `category_pie.png` - Revenue by category pie chart
- `category_bar.png` - Category comparison bar chart
- `customer_segments.png` - Customer segment analysis
- `revenue_by_region.png` - Regional revenue distribution
- `day_of_week.png` - Day of week performance
- `rfm_segments.png` - RFM customer segmentation
- `top_products.png` - Top 10 products by revenue

### 3. Power BI Export
Excel files optimized for Power BI import and dashboard creation.

```bash
python src/export_powerbi.py
```

**Output files:**
- `revenue_analytics.xlsx` - KPIs, monthly trends, category breakdown
- `customer_analytics.xlsx` - Segments, RFM analysis, top customers
- `product_analytics.xlsx` - Top products, category performance
- `geographic_analytics.xlsx` - Regional and country analysis
- `time_analytics.xlsx` - Daily/weekly/monthly trends

## Getting Started

### Installation

```bash
# Clone the repository
git clone https://github.com/ravi-kris/ecommerce-analytics-pipeline.git
cd ecommerce-analytics-pipeline

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Pipeline

```bash
# Generate sample data and run full ETL pipeline
python src/pipeline.py

# Run analytics queries
python src/analytics.py

# Generate HTML dashboard (Plotly)
python src/visualize.py

# Launch Streamlit interactive dashboard
streamlit run app.py

# Generate static charts (Matplotlib)
python src/static_charts.py

# Export data for Power BI
python src/export_powerbi.py
```

## Sample Outputs

### Revenue by Category
The pipeline generates insights like revenue breakdown by product category, identifying top performers.

### Customer Segmentation
RFM (Recency, Frequency, Monetary) analysis segments customers into actionable groups:
- **Champions** - Best customers, high frequency and monetary value
- **Loyal Customers** - Consistent purchasers
- **At Risk** - Previously good customers showing decline
- **Lost** - Inactive customers requiring win-back campaigns

### Sales Trends
Time-series analysis reveals seasonal patterns and growth trends.

## Skills Demonstrated

- **Data Engineering**: ETL pipeline design, data modeling, star schema
- **Python**: pandas, SQLAlchemy, data processing, OOP
- **SQL**: Complex queries, window functions, CTEs, aggregations
- **Data Quality**: Validation, cleaning, handling missing data
- **Visualization**: Multiple platforms (Streamlit, Matplotlib, Power BI)
- **Web Development**: Streamlit interactive applications
- **BI Tools**: Power BI data preparation and export
- **Software Engineering**: Modular code, documentation, version control

## Future Enhancements

- [ ] Add Apache Airflow for orchestration
- [ ] Implement incremental loading
- [ ] Add data quality framework (Great Expectations)
- [x] Deploy dashboard with Streamlit
- [ ] Add unit tests with pytest
- [ ] Add Docker containerization
- [ ] Implement CI/CD pipeline

## License

MIT License
