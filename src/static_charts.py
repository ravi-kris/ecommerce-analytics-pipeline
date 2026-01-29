"""
Static Charts Module (Matplotlib)
---------------------------------
Generates static charts for reports, presentations, and documentation.

Matplotlib is ideal for:
- PDF reports and documentation
- Email attachments
- Print-quality graphics
- Presentations (PowerPoint, Keynote)
- Academic papers and publications

Charts are saved as PNG files with high DPI for quality.

Usage:
    python src/static_charts.py

Output:
    Creates PNG files in the 'reports/charts/' directory.
"""

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
import pandas as pd
import numpy as np
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
    get_day_of_week_analysis,
    get_customer_rfm
)


# ============================================
# Chart Style Configuration
# ============================================

# Set global style for all charts
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

# Custom color palette
COLORS = {
    'primary': '#4F46E5',
    'secondary': '#7C3AED',
    'success': '#22C55E',
    'warning': '#F59E0B',
    'danger': '#EF4444',
    'info': '#3B82F6',
    'gray': '#6B7280'
}

CATEGORY_COLORS = ['#4F46E5', '#7C3AED', '#EC4899', '#F59E0B', '#22C55E']


# ============================================
# Chart Generation Functions
# ============================================

def create_revenue_trend_chart(df: pd.DataFrame, output_path: str) -> None:
    """
    Create monthly revenue trend line chart.

    A clean line chart showing revenue over time with markers
    for each data point and a filled area for visual impact.
    """
    df = df.copy()
    df['month_year'] = df['order_year'].astype(str) + '-' + df['order_month'].astype(str).str.zfill(2)

    fig, ax = plt.subplots(figsize=(12, 6))

    # Plot line with area fill
    ax.plot(df['month_year'], df['revenue'], marker='o', linewidth=2.5,
            color=COLORS['primary'], markersize=6)
    ax.fill_between(df['month_year'], df['revenue'], alpha=0.3, color=COLORS['primary'])

    # Formatting
    ax.set_xlabel('Month', fontsize=12)
    ax.set_ylabel('Revenue ($)', fontsize=12)
    ax.set_title('Monthly Revenue Trend', fontsize=14, fontweight='bold')

    # Format y-axis as currency
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f'${x:,.0f}'))

    # Rotate x-axis labels
    plt.xticks(rotation=45, ha='right')

    # Add grid
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  - Saved: {output_path}")


def create_category_pie_chart(df: pd.DataFrame, output_path: str) -> None:
    """
    Create revenue by category pie chart.

    A donut-style pie chart with percentage labels and
    a clean, professional appearance.
    """
    fig, ax = plt.subplots(figsize=(10, 8))

    # Create pie chart
    wedges, texts, autotexts = ax.pie(
        df['revenue'],
        labels=df['category'],
        autopct='%1.1f%%',
        colors=CATEGORY_COLORS,
        startangle=90,
        explode=[0.02] * len(df),  # Slight separation between slices
        wedgeprops={'linewidth': 2, 'edgecolor': 'white'}
    )

    # Style the text
    for text in texts:
        text.set_fontsize(11)
    for autotext in autotexts:
        autotext.set_fontsize(10)
        autotext.set_fontweight('bold')

    ax.set_title('Revenue by Product Category', fontsize=14, fontweight='bold')

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  - Saved: {output_path}")


def create_category_bar_chart(df: pd.DataFrame, output_path: str) -> None:
    """
    Create horizontal bar chart for category comparison.

    Horizontal bars are easier to read and compare,
    especially when category names are long.
    """
    df = df.sort_values('revenue', ascending=True)

    fig, ax = plt.subplots(figsize=(10, 6))

    bars = ax.barh(df['category'], df['revenue'], color=CATEGORY_COLORS[:len(df)])

    # Add value labels on bars
    for bar, value in zip(bars, df['revenue']):
        ax.text(value + max(df['revenue']) * 0.01, bar.get_y() + bar.get_height()/2,
                f'${value:,.0f}', va='center', fontsize=10)

    ax.set_xlabel('Revenue ($)', fontsize=12)
    ax.set_title('Revenue by Category', fontsize=14, fontweight='bold')

    # Format x-axis
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f'${x/1e6:.1f}M'))

    ax.grid(True, axis='x', alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  - Saved: {output_path}")


def create_customer_segment_chart(df: pd.DataFrame, output_path: str) -> None:
    """
    Create customer segment comparison chart.

    Side-by-side bars comparing customer count and revenue
    contribution by segment.
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Left: Customer count by segment
    ax1 = axes[0]
    bars1 = ax1.bar(df['customer_segment'], df['customers'], color=COLORS['primary'])
    ax1.set_xlabel('Segment', fontsize=12)
    ax1.set_ylabel('Number of Customers', fontsize=12)
    ax1.set_title('Customers by Segment', fontsize=14, fontweight='bold')

    # Add value labels
    for bar in bars1:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height):,}', ha='center', va='bottom', fontsize=10)

    # Right: Revenue by segment
    ax2 = axes[1]
    bars2 = ax2.bar(df['customer_segment'], df['total_revenue'], color=COLORS['secondary'])
    ax2.set_xlabel('Segment', fontsize=12)
    ax2.set_ylabel('Revenue ($)', fontsize=12)
    ax2.set_title('Revenue by Segment', fontsize=14, fontweight='bold')

    # Format y-axis and add labels
    ax2.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f'${x/1e6:.1f}M'))
    for bar in bars2:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'${height/1e6:.1f}M', ha='center', va='bottom', fontsize=10)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  - Saved: {output_path}")


def create_region_chart(df: pd.DataFrame, output_path: str) -> None:
    """
    Create regional revenue bar chart.

    Vertical bars with data labels showing revenue by region.
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    colors = plt.cm.viridis(np.linspace(0.3, 0.8, len(df)))
    bars = ax.bar(df['region'], df['revenue'], color=colors)

    # Add value labels
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'${height:,.0f}', ha='center', va='bottom', fontsize=10)

    ax.set_xlabel('Region', fontsize=12)
    ax.set_ylabel('Revenue ($)', fontsize=12)
    ax.set_title('Revenue by Region', fontsize=14, fontweight='bold')

    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f'${x/1e6:.1f}M'))
    ax.grid(True, axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  - Saved: {output_path}")


def create_day_of_week_chart(df: pd.DataFrame, output_path: str) -> None:
    """
    Create day of week performance dual-axis chart.

    Combines bars (orders) with a line (avg order value)
    to show patterns across days of the week.
    """
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Bar chart for orders
    bars = ax1.bar(df['day_name'], df['orders'], color=COLORS['primary'], alpha=0.7, label='Orders')
    ax1.set_xlabel('Day of Week', fontsize=12)
    ax1.set_ylabel('Number of Orders', fontsize=12, color=COLORS['primary'])
    ax1.tick_params(axis='y', labelcolor=COLORS['primary'])

    # Line chart for avg order value on secondary axis
    ax2 = ax1.twinx()
    ax2.plot(df['day_name'], df['avg_order_value'], color=COLORS['danger'],
             marker='o', linewidth=2.5, markersize=8, label='Avg Order Value')
    ax2.set_ylabel('Avg Order Value ($)', fontsize=12, color=COLORS['danger'])
    ax2.tick_params(axis='y', labelcolor=COLORS['danger'])

    ax1.set_title('Performance by Day of Week', fontsize=14, fontweight='bold')

    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right')

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  - Saved: {output_path}")


def create_rfm_chart(df: pd.DataFrame, output_path: str) -> None:
    """
    Create RFM segment distribution chart.

    Horizontal bar chart showing customer count by RFM segment,
    color-coded by segment health.
    """
    # Aggregate by segment
    segment_counts = df.groupby('customer_segment').size().reset_index(name='count')
    segment_counts = segment_counts.sort_values('count', ascending=True)

    # Color mapping by segment health
    color_map = {
        'Champions': COLORS['success'],
        'Loyal Customers': COLORS['info'],
        'New Customers': '#A855F7',
        'Regular': COLORS['warning'],
        'At Risk': COLORS['danger'],
        'Lost': COLORS['gray']
    }

    colors = [color_map.get(seg, COLORS['gray']) for seg in segment_counts['customer_segment']]

    fig, ax = plt.subplots(figsize=(10, 6))

    bars = ax.barh(segment_counts['customer_segment'], segment_counts['count'], color=colors)

    # Add value labels
    for bar, value in zip(bars, segment_counts['count']):
        ax.text(value + max(segment_counts['count']) * 0.01,
                bar.get_y() + bar.get_height()/2,
                f'{value:,}', va='center', fontsize=10)

    ax.set_xlabel('Number of Customers', fontsize=12)
    ax.set_title('Customer RFM Segmentation', fontsize=14, fontweight='bold')

    ax.grid(True, axis='x', alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  - Saved: {output_path}")


def create_top_products_chart(df: pd.DataFrame, output_path: str) -> None:
    """
    Create top 10 products horizontal bar chart.

    Shows the highest revenue products with category color coding.
    """
    df = df.head(10).sort_values('revenue', ascending=True)

    # Get unique categories and assign colors
    categories = df['category'].unique()
    category_colors = dict(zip(categories, CATEGORY_COLORS[:len(categories)]))
    colors = [category_colors[cat] for cat in df['category']]

    fig, ax = plt.subplots(figsize=(12, 8))

    bars = ax.barh(df['product_name'], df['revenue'], color=colors)

    # Add value labels
    for bar, value in zip(bars, df['revenue']):
        ax.text(value + max(df['revenue']) * 0.01,
                bar.get_y() + bar.get_height()/2,
                f'${value:,.0f}', va='center', fontsize=9)

    ax.set_xlabel('Revenue ($)', fontsize=12)
    ax.set_title('Top 10 Products by Revenue', fontsize=14, fontweight='bold')

    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f'${x/1e3:.0f}K'))
    ax.grid(True, axis='x', alpha=0.3)

    # Add legend for categories
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor=color, label=cat) for cat, color in category_colors.items()]
    ax.legend(handles=legend_elements, loc='lower right', title='Category')

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  - Saved: {output_path}")


# ============================================
# Main Export Function
# ============================================

def generate_static_charts(db_path: str = None, output_dir: str = None) -> None:
    """
    Generate all static charts and save as PNG files.

    Args:
        db_path: Path to the SQLite database
        output_dir: Directory to save chart images
    """
    # Set default paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    if db_path is None:
        db_path = os.path.join(base_dir, 'data', 'warehouse.db')

    if output_dir is None:
        output_dir = os.path.join(base_dir, 'reports', 'charts')

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 60)
    print("Generating Static Charts (Matplotlib)")
    print("=" * 60)

    # Get database connection
    engine = get_engine(db_path)

    # Generate all charts
    print("\nCreating charts...")

    create_revenue_trend_chart(
        get_revenue_by_month(engine),
        os.path.join(output_dir, 'revenue_trend.png')
    )

    create_category_pie_chart(
        get_revenue_by_category(engine),
        os.path.join(output_dir, 'category_pie.png')
    )

    create_category_bar_chart(
        get_revenue_by_category(engine),
        os.path.join(output_dir, 'category_bar.png')
    )

    create_customer_segment_chart(
        get_customer_segments(engine),
        os.path.join(output_dir, 'customer_segments.png')
    )

    create_region_chart(
        get_revenue_by_region(engine),
        os.path.join(output_dir, 'revenue_by_region.png')
    )

    create_day_of_week_chart(
        get_day_of_week_analysis(engine),
        os.path.join(output_dir, 'day_of_week.png')
    )

    create_rfm_chart(
        get_customer_rfm(engine),
        os.path.join(output_dir, 'rfm_segments.png')
    )

    create_top_products_chart(
        get_top_products(engine, limit=10),
        os.path.join(output_dir, 'top_products.png')
    )

    print("\n" + "=" * 60)
    print("Chart Generation Complete!")
    print("=" * 60)
    print(f"\nCharts saved to: {output_dir}/")
    print("""
Available charts:
- revenue_trend.png     : Monthly revenue line chart
- category_pie.png      : Revenue by category pie chart
- category_bar.png      : Revenue by category bar chart
- customer_segments.png : Customer segment comparison
- revenue_by_region.png : Regional revenue bars
- day_of_week.png       : Day of week performance
- rfm_segments.png      : RFM customer segmentation
- top_products.png      : Top 10 products by revenue

Use these charts in:
- PDF reports (LaTeX, Word)
- Presentations (PowerPoint, Keynote)
- Documentation and README files
- Email reports
""")


# ============================================
# Script Entry Point
# ============================================

if __name__ == '__main__':
    generate_static_charts()
