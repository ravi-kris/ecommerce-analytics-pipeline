"""
Streamlit Dashboard
-------------------
Interactive web application for exploring e-commerce analytics.

Streamlit provides a simple way to create data apps with Python.
Run with: streamlit run app.py

Features:
- Real-time filtering and exploration
- Interactive Plotly charts
- KPI metrics display
- Data table views
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# Import analytics functions
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from analytics import (
    get_engine,
    get_total_revenue,
    get_revenue_by_month,
    get_revenue_by_category,
    get_customer_segments,
    get_top_products,
    get_revenue_by_region,
    get_day_of_week_analysis,
    get_customer_rfm,
    get_top_customers
)


# ============================================
# Page Configuration
# ============================================

st.set_page_config(
    page_title="E-commerce Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)


# ============================================
# Data Loading (Cached for Performance)
# ============================================

@st.cache_data
def load_data():
    """Load all analytics data with caching for performance."""
    db_path = os.path.join(os.path.dirname(__file__), 'data', 'warehouse.db')

    if not os.path.exists(db_path):
        st.error("Database not found. Please run the pipeline first: `python src/pipeline.py`")
        st.stop()

    engine = get_engine(db_path)

    return {
        'total_revenue': get_total_revenue(engine),
        'revenue_by_month': get_revenue_by_month(engine),
        'revenue_by_category': get_revenue_by_category(engine),
        'customer_segments': get_customer_segments(engine),
        'top_products': get_top_products(engine, limit=20),
        'revenue_by_region': get_revenue_by_region(engine),
        'day_of_week': get_day_of_week_analysis(engine),
        'customer_rfm': get_customer_rfm(engine),
        'top_customers': get_top_customers(engine, limit=20)
    }


# ============================================
# Sidebar Navigation
# ============================================

st.sidebar.title("📊 Navigation")
page = st.sidebar.radio(
    "Select Page",
    ["Overview", "Revenue Analytics", "Customer Analytics", "Product Analytics"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.info(
    "This dashboard provides interactive analytics for e-commerce data. "
    "Built with Streamlit and Plotly for the Data Engineering Portfolio."
)


# ============================================
# Load Data
# ============================================

data = load_data()


# ============================================
# Overview Page
# ============================================

if page == "Overview":
    st.title("📈 E-commerce Analytics Dashboard")
    st.markdown("Real-time insights into sales, customers, and product performance.")

    # KPI Metrics Row
    st.markdown("### Key Performance Indicators")

    metrics = data['total_revenue'].iloc[0]

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        st.metric("Total Revenue", f"${metrics['total_revenue']:,.0f}")
    with col2:
        st.metric("Total Orders", f"{metrics['total_orders']:,}")
    with col3:
        st.metric("Unique Customers", f"{metrics['unique_customers']:,}")
    with col4:
        st.metric("Avg Order Value", f"${metrics['avg_order_value']:.2f}")
    with col5:
        st.metric("Units Sold", f"{metrics['total_units_sold']:,}")
    with col6:
        st.metric("Total Discounts", f"${metrics['total_discounts']:,.0f}")

    st.markdown("---")

    # Charts Row 1
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Monthly Revenue Trend")
        df = data['revenue_by_month'].copy()
        df['month_year'] = df['order_year'].astype(str) + '-' + df['order_month'].astype(str).str.zfill(2)

        fig = px.line(
            df, x='month_year', y='revenue',
            markers=True,
            title=None
        )
        fig.update_layout(
            xaxis_title="Month",
            yaxis_title="Revenue ($)",
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### Revenue by Category")
        fig = px.pie(
            data['revenue_by_category'],
            values='revenue',
            names='category',
            title=None,
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)

    # Charts Row 2
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Revenue by Region")
        fig = px.bar(
            data['revenue_by_region'],
            x='region', y='revenue',
            color='revenue',
            color_continuous_scale='Viridis',
            title=None
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### Customer Segments")
        fig = px.pie(
            data['customer_segments'],
            values='customers',
            names='customer_segment',
            title=None
        )
        st.plotly_chart(fig, use_container_width=True)


# ============================================
# Revenue Analytics Page
# ============================================

elif page == "Revenue Analytics":
    st.title("💰 Revenue Analytics")

    # Monthly Trend
    st.markdown("### Monthly Revenue Trend")
    df = data['revenue_by_month'].copy()
    df['month_year'] = df['order_year'].astype(str) + '-' + df['order_month'].astype(str).str.zfill(2)

    # Metric selector
    metric_choice = st.selectbox(
        "Select Metric",
        ["revenue", "orders", "customers", "avg_order_value"]
    )

    fig = px.line(
        df, x='month_year', y=metric_choice,
        markers=True,
        title=f"Monthly {metric_choice.replace('_', ' ').title()}"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Category Analysis
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Revenue by Category")
        fig = px.bar(
            data['revenue_by_category'].sort_values('revenue', ascending=True),
            x='revenue', y='category',
            orientation='h',
            color='revenue',
            color_continuous_scale='Blues'
        )
        fig.update_layout(showlegend=False, yaxis_title='')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### Category Performance Table")
        st.dataframe(
            data['revenue_by_category'][['category', 'orders', 'units_sold', 'revenue', 'revenue_pct']].style.format({
                'revenue': '${:,.0f}',
                'revenue_pct': '{:.1f}%'
            }),
            use_container_width=True
        )

    st.markdown("---")

    # Day of Week Analysis
    st.markdown("### Performance by Day of Week")

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Bar(x=data['day_of_week']['day_name'], y=data['day_of_week']['orders'], name="Orders"),
        secondary_y=False
    )

    fig.add_trace(
        go.Scatter(x=data['day_of_week']['day_name'], y=data['day_of_week']['avg_order_value'],
                   name="Avg Order Value", mode='lines+markers'),
        secondary_y=True
    )

    fig.update_layout(
        yaxis_title="Orders",
        yaxis2_title="Avg Order Value ($)"
    )
    st.plotly_chart(fig, use_container_width=True)


# ============================================
# Customer Analytics Page
# ============================================

elif page == "Customer Analytics":
    st.title("👥 Customer Analytics")

    # Customer Segments
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Customer Segments")
        fig = px.bar(
            data['customer_segments'],
            x='customer_segment', y='customers',
            color='total_revenue',
            color_continuous_scale='Viridis',
            title=None
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### Revenue per Customer by Segment")
        fig = px.bar(
            data['customer_segments'],
            x='customer_segment', y='revenue_per_customer',
            color='revenue_per_customer',
            color_continuous_scale='RdYlGn'
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # RFM Analysis
    st.markdown("### RFM Customer Segmentation")
    st.info("RFM (Recency, Frequency, Monetary) analysis segments customers based on their purchasing behavior.")

    rfm_summary = data['customer_rfm'].groupby('customer_segment').size().reset_index(name='count')
    rfm_summary = rfm_summary.sort_values('count', ascending=True)

    colors = {
        'Champions': '#22C55E',
        'Loyal Customers': '#3B82F6',
        'New Customers': '#A855F7',
        'Regular': '#F59E0B',
        'At Risk': '#EF4444',
        'Lost': '#6B7280'
    }

    fig = px.bar(
        rfm_summary,
        x='count', y='customer_segment',
        orientation='h',
        color='customer_segment',
        color_discrete_map=colors
    )
    fig.update_layout(showlegend=False, yaxis_title='')
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Top Customers Table
    st.markdown("### Top 20 Customers")
    st.dataframe(
        data['top_customers'][['customer_id', 'customer_segment', 'region', 'total_orders', 'total_spent', 'avg_order_value']].style.format({
            'total_spent': '${:,.2f}',
            'avg_order_value': '${:,.2f}'
        }),
        use_container_width=True
    )


# ============================================
# Product Analytics Page
# ============================================

elif page == "Product Analytics":
    st.title("📦 Product Analytics")

    # Top Products
    st.markdown("### Top 20 Products by Revenue")

    df = data['top_products'].head(20).sort_values('revenue', ascending=True)

    fig = px.bar(
        df,
        x='revenue', y='product_name',
        orientation='h',
        color='category',
        title=None
    )
    fig.update_layout(yaxis_title='', height=600)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Category Filter
    st.markdown("### Explore Products by Category")

    categories = data['revenue_by_category']['category'].tolist()
    selected_category = st.selectbox("Select Category", ["All"] + categories)

    if selected_category == "All":
        filtered_products = data['top_products']
    else:
        filtered_products = data['top_products'][data['top_products']['category'] == selected_category]

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Products Table")
        st.dataframe(
            filtered_products[['product_name', 'category', 'unit_price', 'units_sold', 'revenue']].style.format({
                'unit_price': '${:.2f}',
                'revenue': '${:,.0f}'
            }),
            use_container_width=True
        )

    with col2:
        st.markdown("#### Revenue Distribution")
        fig = px.histogram(
            filtered_products,
            x='revenue',
            nbins=10,
            title=None
        )
        fig.update_layout(xaxis_title='Revenue ($)', yaxis_title='Count')
        st.plotly_chart(fig, use_container_width=True)


# ============================================
# Footer
# ============================================

st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #888;'>"
    "E-commerce Analytics Pipeline | Data Engineering Portfolio Project"
    "</div>",
    unsafe_allow_html=True
)
