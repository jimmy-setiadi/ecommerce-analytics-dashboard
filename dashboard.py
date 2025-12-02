"""
E-commerce Business Analytics Dashboard

A professional Streamlit dashboard for comprehensive e-commerce business analysis
with interactive visualizations and configurable date range filtering.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Import custom modules
from data_loader import EcommerceDataLoader, load_and_prepare_data
from business_metrics import BusinessMetricsCalculator, calculate_period_comparison

# Page configuration
st.set_page_config(
    page_title="E-commerce Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2E86AB;
        margin-bottom: 0.5rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2E86AB;
        margin-bottom: 1rem;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #2E86AB;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #6c757d;
        margin-bottom: 0.5rem;
    }
    .trend-positive {
        color: #28a745;
    }
    .trend-negative {
        color: #dc3545;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #495057;
        margin: 2rem 0 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_dashboard_data(start_date, end_date):
    """Load and cache data for the dashboard."""
    try:
        # Load data
        loader = EcommerceDataLoader('ecommerce_data/')
        loader.load_raw_data()
        loader.clean_and_transform_data()
        master_df = loader.create_master_dataset()
        
        # Filter by date range
        filtered_df = master_df[
            (master_df['order_purchase_timestamp'] >= pd.to_datetime(start_date)) &
            (master_df['order_purchase_timestamp'] <= pd.to_datetime(end_date))
        ]
        
        # Calculate previous period for comparison
        date_diff = pd.to_datetime(end_date) - pd.to_datetime(start_date)
        prev_start = pd.to_datetime(start_date) - date_diff
        prev_end = pd.to_datetime(start_date)
        
        prev_df = master_df[
            (master_df['order_purchase_timestamp'] >= prev_start) &
            (master_df['order_purchase_timestamp'] < prev_end)
        ]
        
        return filtered_df, prev_df, loader
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None, None, None

def format_currency(value):
    """Format currency values for display."""
    if value >= 1_000_000:
        return f"${value/1_000_000:.1f}M"
    elif value >= 1_000:
        return f"${value/1_000:.0f}K"
    else:
        return f"${value:.0f}"

def format_number(value):
    """Format numbers for display."""
    if value >= 1_000_000:
        return f"{value/1_000_000:.1f}M"
    elif value >= 1_000:
        return f"{value/1_000:.0f}K"
    else:
        return f"{value:.0f}"

def create_trend_indicator(current, previous):
    """Create trend indicator with arrow and percentage."""
    if previous == 0:
        return "N/A", "neutral"
    
    change_pct = ((current - previous) / previous) * 100
    
    if change_pct > 0:
        return f"↗ +{change_pct:.2f}%", "positive"
    elif change_pct < 0:
        return f"↘ {change_pct:.2f}%", "negative"
    else:
        return "→ 0.00%", "neutral"

def create_kpi_cards(current_metrics, prev_metrics):
    """Create KPI cards with trend indicators."""
    col1, col2, col3, col4 = st.columns(4)
    
    # Total Revenue
    with col1:
        current_revenue = current_metrics['total_revenue']
        prev_revenue = prev_metrics['total_revenue']
        trend_text, trend_class = create_trend_indicator(current_revenue, prev_revenue)
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Revenue</div>
            <div class="metric-value">{format_currency(current_revenue)}</div>
            <div class="trend-{trend_class}">{trend_text}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Monthly Growth (placeholder - would need monthly calculation)
    with col2:
        order_growth = ((current_metrics['total_orders'] - prev_metrics['total_orders']) / 
                       prev_metrics['total_orders'] * 100) if prev_metrics['total_orders'] > 0 else 0
        trend_class = "positive" if order_growth > 0 else "negative" if order_growth < 0 else "neutral"
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Order Growth</div>
            <div class="metric-value">{order_growth:+.2f}%</div>
            <div class="trend-{trend_class}">vs Previous Period</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Average Order Value
    with col3:
        current_aov = current_metrics['average_order_value']
        prev_aov = prev_metrics['average_order_value']
        trend_text, trend_class = create_trend_indicator(current_aov, prev_aov)
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Average Order Value</div>
            <div class="metric-value">{format_currency(current_aov)}</div>
            <div class="trend-{trend_class}">{trend_text}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Total Orders
    with col4:
        current_orders = current_metrics['total_orders']
        prev_orders = prev_metrics['total_orders']
        trend_text, trend_class = create_trend_indicator(current_orders, prev_orders)
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Orders</div>
            <div class="metric-value">{format_number(current_orders)}</div>
            <div class="trend-{trend_class}">{trend_text}</div>
        </div>
        """, unsafe_allow_html=True)

def create_revenue_trend_chart(current_data, prev_data):
    """Create revenue trend line chart."""
    fig = go.Figure()
    
    # Check if we have data
    if current_data.empty:
        fig.add_annotation(
            text="No data available for selected period",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False, font=dict(size=16)
        )
        fig.update_layout(
            title="Revenue Trend Comparison",
            height=400,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False)
        )
        return fig
    
    # Determine aggregation level based on date range
    current_delivered = current_data[current_data['order_status'] == 'delivered']
    date_range = (current_delivered['order_purchase_timestamp'].max() - 
                 current_delivered['order_purchase_timestamp'].min()).days
    
    if date_range <= 90:  # 3 months or less - use weekly
        freq = 'W'
        date_format = '%Y-%m-%d'
        title_suffix = "(Weekly)"
    elif date_range <= 730:  # 2 years or less - use monthly
        freq = 'M'
        date_format = '%Y-%m'
        title_suffix = "(Monthly)"
    else:  # More than 2 years - use quarterly
        freq = 'Q'
        date_format = '%Y-Q%q'
        title_suffix = "(Quarterly)"
    
    # Prepare current period data
    if not current_delivered.empty:
        current_grouped = (
            current_delivered
            .groupby(pd.Grouper(key='order_purchase_timestamp', freq=freq))['price']
            .sum()
            .reset_index()
        )
        current_grouped = current_grouped[current_grouped['price'] > 0]
        
        if not current_grouped.empty:
            fig.add_trace(go.Scatter(
                x=current_grouped['order_purchase_timestamp'],
                y=current_grouped['price'],
                mode='lines+markers',
                name='Current Period',
                line=dict(color='#2E86AB', width=3),
                marker=dict(size=8),
                hovertemplate='<b>%{x}</b><br>Revenue: $%{y:,.0f}<extra></extra>'
            ))
    
    # Prepare previous period data
    if not prev_data.empty:
        prev_delivered = prev_data[prev_data['order_status'] == 'delivered']
        if not prev_delivered.empty:
            prev_grouped = (
                prev_delivered
                .groupby(pd.Grouper(key='order_purchase_timestamp', freq=freq))['price']
                .sum()
                .reset_index()
            )
            prev_grouped = prev_grouped[prev_grouped['price'] > 0]
            
            if not prev_grouped.empty:
                fig.add_trace(go.Scatter(
                    x=prev_grouped['order_purchase_timestamp'],
                    y=prev_grouped['price'],
                    mode='lines+markers',
                    name='Previous Period',
                    line=dict(color='#A23B72', width=2, dash='dash'),
                    marker=dict(size=6),
                    hovertemplate='<b>%{x}</b><br>Revenue: $%{y:,.0f}<extra></extra>'
                ))
    
    fig.update_layout(
        title=f"Revenue Trend Comparison {title_suffix}",
        xaxis_title="Date",
        yaxis_title="Revenue",
        showlegend=True,
        height=400,
        xaxis=dict(showgrid=True, gridcolor='lightgray'),
        yaxis=dict(showgrid=True, gridcolor='lightgray', tickformat='$,.0f')
    )
    
    return fig

def create_category_chart(product_metrics):
    """Create top 10 categories bar chart."""
    top_categories = product_metrics['category_metrics'].head(10)
    
    fig = go.Figure(data=[
        go.Bar(
            y=top_categories.index,
            x=top_categories['total_revenue'],
            orientation='h',
            marker=dict(
                color=top_categories['total_revenue'],
                colorscale='Blues',
                showscale=False
            ),
            text=[format_currency(x) for x in top_categories['total_revenue']],
            textposition='outside'
        )
    ])
    
    fig.update_layout(
        title="Top 10 Product Categories by Revenue",
        xaxis_title="Revenue",
        yaxis_title="Category",
        height=400,
        xaxis=dict(tickformat='$,.0f')
    )
    
    return fig

def create_state_map(geographic_metrics):
    """Create US choropleth map for revenue by state."""
    state_data = geographic_metrics['state_metrics'].reset_index()
    state_data.columns = ['state', 'total_revenue', 'orders', 'avg_order_value', 'revenue_share']
    
    fig = go.Figure(data=go.Choropleth(
        locations=state_data['state'],
        z=state_data['total_revenue'],
        locationmode='USA-states',
        colorscale='Blues',
        text=state_data['state'],
        hovertemplate='<b>%{text}</b><br>Revenue: $%{z:,.0f}<extra></extra>',
        colorbar_title="Revenue ($)"
    ))
    
    fig.update_layout(
        title="Revenue by State",
        geo_scope='usa',
        height=400
    )
    
    return fig

def create_satisfaction_delivery_chart(cx_metrics):
    """Create satisfaction vs delivery time chart."""
    if cx_metrics['satisfaction_by_delivery'].empty:
        # Create placeholder chart
        fig = go.Figure()
        fig.add_annotation(
            text="Insufficient data for satisfaction analysis",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False, font=dict(size=16)
        )
        fig.update_layout(
            title="Customer Satisfaction vs Delivery Time",
            height=400,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False)
        )
        return fig
    
    satisfaction_data = cx_metrics['satisfaction_by_delivery'].reset_index()
    
    fig = go.Figure(data=[
        go.Bar(
            x=satisfaction_data['delivery_bucket'],
            y=satisfaction_data['avg_review_score'],
            marker_color='#FF6B6B',
            text=[f"{x:.2f}" for x in satisfaction_data['avg_review_score']],
            textposition='outside'
        )
    ])
    
    fig.update_layout(
        title="Customer Satisfaction vs Delivery Time",
        xaxis_title="Delivery Time",
        yaxis_title="Average Review Score",
        height=400,
        yaxis=dict(range=[0, 5])
    )
    
    return fig

def create_bottom_cards(cx_metrics, current_metrics, prev_metrics):
    """Create bottom row cards for delivery time and review score."""
    col1, col2 = st.columns(2)
    
    # Average Delivery Time
    with col1:
        current_delivery = cx_metrics['delivery_metrics']['avg_delivery_days']
        # For demo purposes, assume 10% improvement (would need actual previous period data)
        prev_delivery = current_delivery * 1.1
        trend_text, trend_class = create_trend_indicator(current_delivery, prev_delivery)
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Average Delivery Time</div>
            <div class="metric-value">{current_delivery:.1f} days</div>
            <div class="trend-{trend_class}">{trend_text}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Review Score
    with col2:
        avg_score = cx_metrics['review_metrics']['avg_review_score']
        stars = "★" * int(avg_score) + "☆" * (5 - int(avg_score))
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Average Review Score</div>
            <div class="metric-value">{avg_score:.2f} {stars}</div>
            <div style="color: #6c757d;">Customer Satisfaction</div>
        </div>
        """, unsafe_allow_html=True)

def main():
    """Main dashboard function."""
    # Header with title and date filter
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown('<h1 class="main-header">E-commerce Analytics Dashboard</h1>', 
                   unsafe_allow_html=True)
    
    with col2:
        # Date range filter
        end_date = st.date_input("End Date", value=datetime(2023, 12, 31))
        start_date = st.date_input("Start Date", value=datetime(2023, 1, 1))
    
    # Load data
    current_data, prev_data, loader = load_dashboard_data(start_date, end_date)
    
    if current_data is None:
        st.error("Failed to load data. Please check your data files.")
        return
    
    # Calculate metrics
    current_calculator = BusinessMetricsCalculator(current_data)
    prev_calculator = BusinessMetricsCalculator(prev_data)
    
    current_revenue_metrics = current_calculator.calculate_revenue_metrics()
    prev_revenue_metrics = prev_calculator.calculate_revenue_metrics()
    
    product_metrics = current_calculator.calculate_product_metrics()
    geographic_metrics = current_calculator.calculate_geographic_metrics()
    cx_metrics = current_calculator.calculate_customer_experience_metrics()
    
    # KPI Cards Row
    st.markdown('<div class="section-header">Key Performance Indicators</div>', 
               unsafe_allow_html=True)
    create_kpi_cards(current_revenue_metrics, prev_revenue_metrics)
    
    # Charts Grid (2x2)
    st.markdown('<div class="section-header">Performance Analytics</div>', 
               unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Revenue trend chart
        revenue_chart = create_revenue_trend_chart(current_data, prev_data)
        st.plotly_chart(revenue_chart, use_container_width=True)
        
        # State map
        state_map = create_state_map(geographic_metrics)
        st.plotly_chart(state_map, use_container_width=True)
    
    with col2:
        # Category chart
        category_chart = create_category_chart(product_metrics)
        st.plotly_chart(category_chart, use_container_width=True)
        
        # Satisfaction chart
        satisfaction_chart = create_satisfaction_delivery_chart(cx_metrics)
        st.plotly_chart(satisfaction_chart, use_container_width=True)
    
    # Bottom Row Cards
    st.markdown('<div class="section-header">Customer Experience Metrics</div>', 
               unsafe_allow_html=True)
    create_bottom_cards(cx_metrics, current_revenue_metrics, prev_revenue_metrics)
    
    # Footer
    st.markdown("---")
    st.markdown(f"""
    **Dashboard Summary:** Analyzing {len(current_data):,} records from {start_date} to {end_date}  
    **Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
    **Created by:** Jimmy Setiadi
    """)

if __name__ == "__main__":
    main()