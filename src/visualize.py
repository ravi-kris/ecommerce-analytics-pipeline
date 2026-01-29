"""
Visualization Module
--------------------
Creates interactive charts and dashboards from analytics data.
Generates HTML reports with embedded visualizations.

This module demonstrates:
- Interactive visualizations with Plotly
- Dashboard design principles
- HTML report generation with Jinja2 templates
- Data storytelling through visualization

In production, these visualizations could be deployed via:
- Streamlit or Dash for interactive web apps
- Embedded in BI tools (Looker, Tableau)
- Automated email reports
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from datetime import datetime
from jinja2 import Template

# Import analytics functions to fetch data
from analytics import (
    get_engine,
    get_total_revenue,
    get_revenue_by_month,
    get_revenue_by_category,
    get_customer_segments,
    get_top_products,
    get_revenue_by_region,
    get_day_of_week_analysis,
    get_customer_rfm
)


# ============================================
# Chart Creation Functions
# ============================================

def create_revenue_trend_chart(df: pd.DataFrame) -> str:
    """
    Create monthly revenue trend line chart.

    Line charts are ideal for showing trends over time.
    The combination of lines and markers helps identify
    both the trend and individual data points.
    """
    df = df.copy()
    # Create a formatted month-year string for the x-axis
    df['month_year'] = df['order_year'].astype(str) + '-' + df['order_month'].astype(str).str.zfill(2)

    fig = go.Figure()

    # Add line trace with markers
    fig.add_trace(go.Scatter(
        x=df['month_year'],
        y=df['revenue'],
        mode='lines+markers',  # Show both line and points
        name='Revenue',
        line=dict(color='#4F46E5', width=3),
        marker=dict(size=8)
    ))

    # Configure layout for clean presentation
    fig.update_layout(
        title='Monthly Revenue Trend',
        xaxis_title='Month',
        yaxis_title='Revenue ($)',
        template='plotly_white',  # Clean white background
        hovermode='x unified'     # Show all values at x position
    )

    # Return as embeddable HTML (not full page)
    return fig.to_html(full_html=False, include_plotlyjs=False)


def create_category_pie_chart(df: pd.DataFrame) -> str:
    """
    Create revenue by category pie chart.

    Pie charts show part-to-whole relationships.
    Best used when showing composition of a total.
    """
    fig = px.pie(
        df,
        values='revenue',
        names='category',
        title='Revenue by Product Category',
        color_discrete_sequence=px.colors.qualitative.Set2
    )

    # Show percentage and label inside slices
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(template='plotly_white')

    return fig.to_html(full_html=False, include_plotlyjs=False)


def create_category_bar_chart(df: pd.DataFrame) -> str:
    """
    Create revenue by category horizontal bar chart.

    Horizontal bars are easier to read when category names are long.
    Color gradient reinforces the ranking visually.
    """
    fig = px.bar(
        df.sort_values('revenue', ascending=True),  # Sort for visual hierarchy
        x='revenue',
        y='category',
        orientation='h',
        title='Revenue by Category',
        color='revenue',
        color_continuous_scale='Blues'  # Gradient shows magnitude
    )

    fig.update_layout(
        template='plotly_white',
        showlegend=False,
        yaxis_title='',
        xaxis_title='Revenue ($)'
    )

    return fig.to_html(full_html=False, include_plotlyjs=False)


def create_customer_segment_chart(df: pd.DataFrame) -> str:
    """
    Create customer segment analysis chart with dual pie charts.

    Shows both customer count and revenue distribution by segment.
    This reveals if high-value segments are proportionally larger.
    """
    # Create side-by-side subplots
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Customers by Segment', 'Revenue by Segment'),
        specs=[[{"type": "pie"}, {"type": "pie"}]]
    )

    # Left pie: Customer distribution
    fig.add_trace(
        go.Pie(labels=df['customer_segment'], values=df['customers'], name='Customers'),
        row=1, col=1
    )

    # Right pie: Revenue distribution
    fig.add_trace(
        go.Pie(labels=df['customer_segment'], values=df['total_revenue'], name='Revenue'),
        row=1, col=2
    )

    fig.update_layout(template='plotly_white', title_text='Customer Segment Analysis')

    return fig.to_html(full_html=False, include_plotlyjs=False)


def create_top_products_chart(df: pd.DataFrame) -> str:
    """
    Create top products horizontal bar chart.

    Color-coded by category to show which categories
    dominate the top performers.
    """
    df = df.head(10).sort_values('revenue', ascending=True)

    fig = px.bar(
        df,
        x='revenue',
        y='product_name',
        orientation='h',
        title='Top 10 Products by Revenue',
        color='category',  # Color by category for additional insight
        color_discrete_sequence=px.colors.qualitative.Pastel
    )

    fig.update_layout(
        template='plotly_white',
        yaxis_title='',
        xaxis_title='Revenue ($)',
        legend_title='Category'
    )

    return fig.to_html(full_html=False, include_plotlyjs=False)


def create_region_chart(df: pd.DataFrame) -> str:
    """
    Create revenue by region bar chart.

    Includes data labels for exact values.
    Color gradient reinforces regional performance.
    """
    fig = px.bar(
        df,
        x='region',
        y='revenue',
        title='Revenue by Region',
        color='revenue',
        color_continuous_scale='Viridis',
        text='revenue'  # Show value on bars
    )

    # Format text labels as currency
    fig.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
    fig.update_layout(
        template='plotly_white',
        showlegend=False,
        xaxis_title='Region',
        yaxis_title='Revenue ($)'
    )

    return fig.to_html(full_html=False, include_plotlyjs=False)


def create_day_of_week_chart(df: pd.DataFrame) -> str:
    """
    Create day of week performance chart with dual axis.

    Combines bar chart (orders) with line chart (avg order value).
    Dual axis reveals if order volume correlates with order size.
    """
    fig = go.Figure()

    # Primary axis: Order count as bars
    fig.add_trace(go.Bar(
        x=df['day_name'],
        y=df['orders'],
        name='Orders',
        marker_color='#4F46E5'
    ))

    # Secondary axis: Average order value as line
    fig.add_trace(go.Scatter(
        x=df['day_name'],
        y=df['avg_order_value'],
        name='Avg Order Value',
        yaxis='y2',  # Use secondary y-axis
        line=dict(color='#EF4444', width=3),
        marker=dict(size=10)
    ))

    fig.update_layout(
        title='Performance by Day of Week',
        template='plotly_white',
        yaxis=dict(title='Number of Orders'),
        yaxis2=dict(title='Avg Order Value ($)', overlaying='y', side='right'),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )

    return fig.to_html(full_html=False, include_plotlyjs=False)


def create_rfm_chart(df: pd.DataFrame) -> str:
    """
    Create RFM segment distribution chart.

    Color-coded by segment type to quickly identify
    customer health distribution.
    """
    # Aggregate by segment
    segment_counts = df.groupby('customer_segment').size().reset_index(name='count')
    segment_counts = segment_counts.sort_values('count', ascending=True)

    # Meaningful colors for each segment
    colors = {
        'Champions': '#22C55E',       # Green - best customers
        'Loyal Customers': '#3B82F6', # Blue - valuable
        'New Customers': '#A855F7',   # Purple - potential
        'Regular': '#F59E0B',         # Yellow - neutral
        'At Risk': '#EF4444',         # Red - needs attention
        'Lost': '#6B7280'             # Gray - inactive
    }

    fig = px.bar(
        segment_counts,
        x='count',
        y='customer_segment',
        orientation='h',
        title='Customer RFM Segmentation',
        color='customer_segment',
        color_discrete_map=colors
    )

    fig.update_layout(
        template='plotly_white',
        showlegend=False,
        yaxis_title='',
        xaxis_title='Number of Customers'
    )

    return fig.to_html(full_html=False, include_plotlyjs=False)


# ============================================
# HTML Report Template
# ============================================

# Jinja2 template for the dashboard HTML
# Uses CSS Grid for responsive layout
REPORT_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>E-commerce Analytics Dashboard</title>
    <!-- Plotly.js for interactive charts -->
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        /* Reset and base styles */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f3f4f6;
            color: #1f2937;
            line-height: 1.6;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }

        /* Header styling */
        header {
            background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
            color: white;
            padding: 30px;
            margin-bottom: 30px;
            border-radius: 12px;
        }

        header h1 {
            font-size: 2rem;
            margin-bottom: 10px;
        }

        header p {
            opacity: 0.9;
        }

        /* KPI metric cards - responsive grid */
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .metric-card {
            background: white;
            padding: 24px;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }

        .metric-card h3 {
            font-size: 0.875rem;
            color: #6b7280;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }

        .metric-card .value {
            font-size: 2rem;
            font-weight: 700;
            color: #1f2937;
        }

        /* Chart grid layout */
        .chart-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .chart-card {
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }

        /* Full-width chart spans all columns */
        .chart-full {
            grid-column: 1 / -1;
        }

        footer {
            text-align: center;
            padding: 20px;
            color: #6b7280;
            font-size: 0.875rem;
        }

        /* Mobile responsiveness */
        @media (max-width: 768px) {
            .chart-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Dashboard Header -->
        <header>
            <h1>E-commerce Analytics Dashboard</h1>
            <p>Generated on {{ generated_date }}</p>
        </header>

        <!-- KPI Metrics Row -->
        <div class="metrics-grid">
            <div class="metric-card">
                <h3>Total Revenue</h3>
                <div class="value">${{ "{:,.0f}".format(total_revenue) }}</div>
            </div>
            <div class="metric-card">
                <h3>Total Orders</h3>
                <div class="value">{{ "{:,}".format(total_orders) }}</div>
            </div>
            <div class="metric-card">
                <h3>Unique Customers</h3>
                <div class="value">{{ "{:,}".format(unique_customers) }}</div>
            </div>
            <div class="metric-card">
                <h3>Avg Order Value</h3>
                <div class="value">${{ "{:,.2f}".format(avg_order_value) }}</div>
            </div>
            <div class="metric-card">
                <h3>Units Sold</h3>
                <div class="value">{{ "{:,}".format(total_units) }}</div>
            </div>
            <div class="metric-card">
                <h3>Total Discounts</h3>
                <div class="value">${{ "{:,.0f}".format(total_discounts) }}</div>
            </div>
        </div>

        <!-- Charts Grid -->
        <div class="chart-grid">
            <!-- Revenue trend spans full width -->
            <div class="chart-card chart-full">
                {{ revenue_trend_chart | safe }}
            </div>

            <!-- Category analysis - two charts side by side -->
            <div class="chart-card">
                {{ category_pie_chart | safe }}
            </div>

            <div class="chart-card">
                {{ category_bar_chart | safe }}
            </div>

            <!-- Customer analysis -->
            <div class="chart-card">
                {{ customer_segment_chart | safe }}
            </div>

            <div class="chart-card">
                {{ rfm_chart | safe }}
            </div>

            <!-- Top products spans full width -->
            <div class="chart-card chart-full">
                {{ top_products_chart | safe }}
            </div>

            <!-- Regional and temporal analysis -->
            <div class="chart-card">
                {{ region_chart | safe }}
            </div>

            <div class="chart-card">
                {{ day_of_week_chart | safe }}
            </div>
        </div>

        <footer>
            <p>E-commerce Analytics Pipeline - Data Engineering Portfolio Project</p>
        </footer>
    </div>
</body>
</html>
"""


# ============================================
# Dashboard Generation
# ============================================

def generate_dashboard(db_path: str = 'data/warehouse.db', output_dir: str = 'reports') -> str:
    """
    Generate interactive HTML dashboard with all visualizations.

    This function orchestrates the entire dashboard generation process:
    1. Fetch data from the data warehouse
    2. Create all visualizations
    3. Render the HTML template
    4. Save to file

    Args:
        db_path: Path to the SQLite database
        output_dir: Directory to save the report

    Returns:
        Path to the generated report
    """
    print("Generating dashboard...")

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Get database connection
    engine = get_engine(db_path)

    # ---- Fetch Data ----
    print("  - Fetching analytics data...")
    total_revenue_df = get_total_revenue(engine)
    revenue_by_month = get_revenue_by_month(engine)
    revenue_by_category = get_revenue_by_category(engine)
    customer_segments = get_customer_segments(engine)
    top_products = get_top_products(engine)
    revenue_by_region = get_revenue_by_region(engine)
    day_of_week = get_day_of_week_analysis(engine)
    customer_rfm = get_customer_rfm(engine)

    # ---- Create Charts ----
    print("  - Creating visualizations...")
    charts = {
        'revenue_trend_chart': create_revenue_trend_chart(revenue_by_month),
        'category_pie_chart': create_category_pie_chart(revenue_by_category),
        'category_bar_chart': create_category_bar_chart(revenue_by_category),
        'customer_segment_chart': create_customer_segment_chart(customer_segments),
        'top_products_chart': create_top_products_chart(top_products),
        'region_chart': create_region_chart(revenue_by_region),
        'day_of_week_chart': create_day_of_week_chart(day_of_week),
        'rfm_chart': create_rfm_chart(customer_rfm)
    }

    # ---- Prepare Template Data ----
    template_data = {
        'generated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total_revenue': total_revenue_df['total_revenue'].iloc[0],
        'total_orders': int(total_revenue_df['total_orders'].iloc[0]),
        'unique_customers': int(total_revenue_df['unique_customers'].iloc[0]),
        'avg_order_value': total_revenue_df['avg_order_value'].iloc[0],
        'total_units': int(total_revenue_df['total_units_sold'].iloc[0]),
        'total_discounts': total_revenue_df['total_discounts'].iloc[0],
        **charts  # Merge chart HTML into template data
    }

    # ---- Render Template ----
    print("  - Rendering report...")
    template = Template(REPORT_TEMPLATE)
    html_content = template.render(**template_data)

    # ---- Save Report ----
    report_path = os.path.join(output_dir, 'dashboard.html')
    with open(report_path, 'w') as f:
        f.write(html_content)

    print(f"Dashboard saved to {report_path}")
    return report_path


# ============================================
# Script Entry Point
# ============================================

if __name__ == '__main__':
    generate_dashboard()
