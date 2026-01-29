# E-commerce Sales Analytics Pipeline

A data engineering portfolio project demonstrating ETL pipelines, data modeling, SQL analytics, and visualization.

## Project Overview

This project simulates a real-world data engineering workflow for an e-commerce company, including:

- **Data Ingestion**: Extract data from CSV files and APIs
- **Data Transformation**: Clean, validate, and transform raw data
- **Data Loading**: Load processed data into a SQLite data warehouse
- **Analytics**: SQL-based business intelligence queries
- **Visualization**: Interactive dashboards and automated reports

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Sources   │────▶│   Extract   │────▶│  Transform  │────▶│    Load     │
│  (CSV/API)  │     │             │     │   & Clean   │     │  (SQLite)   │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                                                                   │
                                                                   ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Reports   │◀────│  Visualize  │◀────│  Analytics  │◀────│    Query    │
│   (HTML)    │     │  (Plotly)   │     │    (SQL)    │     │             │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

## Tech Stack

- **Python 3.10+**
- **pandas** - Data manipulation and analysis
- **SQLAlchemy** - Database ORM and SQL toolkit
- **SQLite** - Lightweight data warehouse
- **Plotly/Seaborn** - Data visualization
- **Jinja2** - Report templating

## Project Structure

```
ecommerce-analytics-pipeline/
├── data/
│   ├── raw/              # Raw source data
│   ├── processed/        # Cleaned data
│   └── warehouse.db      # SQLite database
├── src/
│   ├── extract.py        # Data extraction module
│   ├── transform.py      # Data transformation & cleaning
│   ├── load.py           # Database loading module
│   ├── analytics.py      # SQL analytics queries
│   ├── visualize.py      # Dashboard generation
│   └── pipeline.py       # Main ETL orchestrator
├── notebooks/
│   └── exploration.ipynb # Data exploration notebook
├── reports/              # Generated HTML reports
├── requirements.txt
└── README.md
```

## Data Model

### Dimension Tables
- **dim_customers** - Customer demographics
- **dim_products** - Product catalog
- **dim_date** - Date dimension for time-based analysis

### Fact Tables
- **fact_orders** - Order transactions with metrics

## Key Metrics

- Total Revenue & Average Order Value
- Customer Lifetime Value (CLV)
- Product Performance Analysis
- Sales Trends (Daily/Monthly/Quarterly)
- Customer Segmentation (RFM Analysis)
- Geographic Sales Distribution

## Getting Started

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ecommerce-analytics-pipeline.git
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

# Generate visualization dashboard
python src/visualize.py
```

## Sample Outputs

### Revenue by Category
The pipeline generates insights like revenue breakdown by product category, identifying top performers.

### Customer Segmentation
RFM (Recency, Frequency, Monetary) analysis segments customers into actionable groups.

### Sales Trends
Time-series analysis reveals seasonal patterns and growth trends.

## Skills Demonstrated

- **Data Engineering**: ETL pipeline design, data modeling, schema design
- **Python**: pandas, SQLAlchemy, data processing
- **SQL**: Complex queries, window functions, CTEs, aggregations
- **Data Quality**: Validation, cleaning, handling missing data
- **Visualization**: Interactive charts, automated reporting
- **Software Engineering**: Modular code, documentation, version control

## Future Enhancements

- [ ] Add Apache Airflow for orchestration
- [ ] Implement incremental loading
- [ ] Add data quality framework (Great Expectations)
- [ ] Deploy dashboard with Streamlit
- [ ] Add unit tests with pytest

## License

MIT License
