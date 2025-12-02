"""
Business Metrics Calculation Module for E-commerce Analysis

This module contains functions to calculate key business metrics including
revenue analysis, customer metrics, product performance, and operational KPIs.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta


class BusinessMetricsCalculator:
    """
    A class to calculate various business metrics for e-commerce analysis.
    
    This class provides methods to compute revenue metrics, customer analytics,
    product performance, geographic analysis, and operational metrics.
    """
    
    def __init__(self, data: pd.DataFrame):
        """
        Initialize the calculator with the master dataset.
        
        Args:
            data (pd.DataFrame): Master dataset containing all joined information
        """
        self.data = data
        self.delivered_orders = data[data['order_status'] == 'delivered'].copy()
    
    def calculate_revenue_metrics(self, 
                                comparison_period: Optional[pd.DataFrame] = None) -> Dict:
        """
        Calculate comprehensive revenue metrics.
        
        Args:
            comparison_period (pd.DataFrame, optional): Data for comparison period
            
        Returns:
            Dict: Revenue metrics including totals, growth, and trends
        """
        current_data = self.delivered_orders
        
        metrics = {
            'total_revenue': current_data['price'].sum(),
            'total_orders': current_data['order_id'].nunique(),
            'total_items_sold': len(current_data),
            'average_order_value': current_data.groupby('order_id')['price'].sum().mean(),
            'average_item_price': current_data['price'].mean(),
        }
        
        # Monthly revenue trend
        monthly_revenue = (
            current_data.groupby(['order_year', 'order_month'])['price']
            .sum()
            .reset_index()
        )
        monthly_revenue['year_month'] = (
            monthly_revenue['order_year'].astype(str) + '-' + 
            monthly_revenue['order_month'].astype(str).str.zfill(2)
        )
        metrics['monthly_revenue_trend'] = monthly_revenue
        
        # Calculate growth metrics if comparison period provided
        if comparison_period is not None:
            comparison_delivered = comparison_period[
                comparison_period['order_status'] == 'delivered'
            ]
            
            prev_revenue = comparison_delivered['price'].sum()
            prev_orders = comparison_delivered['order_id'].nunique()
            prev_aov = comparison_delivered.groupby('order_id')['price'].sum().mean()
            
            metrics['revenue_growth'] = (
                (metrics['total_revenue'] - prev_revenue) / prev_revenue * 100
                if prev_revenue > 0 else 0
            )
            metrics['order_growth'] = (
                (metrics['total_orders'] - prev_orders) / prev_orders * 100
                if prev_orders > 0 else 0
            )
            metrics['aov_growth'] = (
                (metrics['average_order_value'] - prev_aov) / prev_aov * 100
                if prev_aov > 0 else 0
            )
        
        return metrics
    
    def calculate_product_metrics(self) -> Dict:
        """
        Calculate product-related business metrics.
        
        Returns:
            Dict: Product performance metrics
        """
        current_data = self.delivered_orders
        
        # Revenue by category
        category_revenue = (
            current_data.groupby('category_clean')['price']
            .agg(['sum', 'count', 'mean'])
            .round(2)
            .sort_values('sum', ascending=False)
        )
        category_revenue.columns = ['total_revenue', 'items_sold', 'avg_price']
        
        # Top products by revenue
        product_revenue = (
            current_data.groupby('product_id')['price']
            .agg(['sum', 'count'])
            .sort_values('sum', ascending=False)
            .head(20)
        )
        product_revenue.columns = ['total_revenue', 'items_sold']
        
        # Category performance metrics
        category_metrics = category_revenue.copy()
        category_metrics['revenue_share'] = (
            category_metrics['total_revenue'] / 
            category_metrics['total_revenue'].sum() * 100
        ).round(2)
        
        return {
            'category_revenue': category_revenue,
            'category_metrics': category_metrics,
            'top_products': product_revenue,
            'total_categories': current_data['category_clean'].nunique(),
            'total_products': current_data['product_id'].nunique()
        }
    
    def calculate_geographic_metrics(self) -> Dict:
        """
        Calculate geographic distribution metrics.
        
        Returns:
            Dict: Geographic performance metrics
        """
        current_data = self.delivered_orders
        
        # Revenue by state
        state_revenue = (
            current_data.groupby('customer_state')['price']
            .agg(['sum', 'count', 'mean'])
            .round(2)
            .sort_values('sum', ascending=False)
        )
        state_revenue.columns = ['total_revenue', 'orders', 'avg_order_value']
        
        # Revenue by city (top 20)
        city_revenue = (
            current_data.groupby(['customer_state', 'customer_city'])['price']
            .sum()
            .sort_values(ascending=False)
            .head(20)
            .reset_index()
        )
        
        # Geographic distribution metrics
        state_metrics = state_revenue.copy()
        state_metrics['revenue_share'] = (
            state_metrics['total_revenue'] / 
            state_metrics['total_revenue'].sum() * 100
        ).round(2)
        
        return {
            'state_revenue': state_revenue,
            'state_metrics': state_metrics,
            'top_cities': city_revenue,
            'total_states': current_data['customer_state'].nunique(),
            'total_cities': current_data['customer_city'].nunique()
        }
    
    def calculate_customer_experience_metrics(self) -> Dict:
        """
        Calculate customer experience and satisfaction metrics.
        
        Returns:
            Dict: Customer experience metrics
        """
        current_data = self.delivered_orders
        
        # Delivery performance
        delivery_data = current_data.dropna(subset=['delivery_days'])
        
        delivery_metrics = {
            'avg_delivery_days': delivery_data['delivery_days'].mean(),
            'median_delivery_days': delivery_data['delivery_days'].median(),
            'delivery_std': delivery_data['delivery_days'].std(),
            'on_time_delivery_rate': None  # Would need estimated vs actual comparison
        }
        
        # Create delivery time buckets
        delivery_data_copy = delivery_data.copy()
        delivery_data_copy['delivery_bucket'] = pd.cut(
            delivery_data_copy['delivery_days'],
            bins=[0, 3, 7, 14, 30, float('inf')],
            labels=['1-3 days', '4-7 days', '8-14 days', '15-30 days', '30+ days'],
            include_lowest=True
        )
        
        delivery_distribution = (
            delivery_data_copy['delivery_bucket']
            .value_counts()
            .sort_index()
        )
        
        # Review metrics
        review_data = current_data.dropna(subset=['review_score'])
        
        review_metrics = {
            'avg_review_score': review_data['review_score'].mean(),
            'review_distribution': review_data['review_score'].value_counts().sort_index(),
            'total_reviews': len(review_data),
            'review_rate': len(review_data) / len(current_data) * 100
        }
        
        # Satisfaction by delivery time
        if not review_data.empty and not delivery_data.empty:
            satisfaction_by_delivery = (
                current_data.dropna(subset=['review_score', 'delivery_days'])
                .copy()
            )
            satisfaction_by_delivery['delivery_bucket'] = pd.cut(
                satisfaction_by_delivery['delivery_days'],
                bins=[0, 3, 7, 14, 30, float('inf')],
                labels=['1-3 days', '4-7 days', '8-14 days', '15-30 days', '30+ days'],
                include_lowest=True
            )
            
            satisfaction_metrics = (
                satisfaction_by_delivery.groupby('delivery_bucket')['review_score']
                .agg(['mean', 'count'])
                .round(2)
            )
            satisfaction_metrics.columns = ['avg_review_score', 'review_count']
        else:
            satisfaction_metrics = pd.DataFrame()
        
        return {
            'delivery_metrics': delivery_metrics,
            'delivery_distribution': delivery_distribution,
            'review_metrics': review_metrics,
            'satisfaction_by_delivery': satisfaction_metrics
        }
    
    def calculate_operational_metrics(self) -> Dict:
        """
        Calculate operational performance metrics.
        
        Returns:
            Dict: Operational metrics
        """
        all_orders = self.data
        delivered_orders = self.delivered_orders
        
        # Order status distribution
        status_distribution = all_orders['order_status'].value_counts()
        status_percentages = (status_distribution / len(all_orders) * 100).round(2)
        
        # Fulfillment metrics
        fulfillment_rate = len(delivered_orders) / len(all_orders) * 100
        
        # Cancellation analysis
        canceled_orders = all_orders[all_orders['order_status'] == 'canceled']
        cancellation_rate = len(canceled_orders) / len(all_orders) * 100
        
        # Return analysis
        returned_orders = all_orders[all_orders['order_status'] == 'returned']
        return_rate = len(returned_orders) / len(delivered_orders) * 100 if len(delivered_orders) > 0 else 0
        
        return {
            'order_status_distribution': status_distribution,
            'order_status_percentages': status_percentages,
            'fulfillment_rate': fulfillment_rate,
            'cancellation_rate': cancellation_rate,
            'return_rate': return_rate,
            'total_orders': len(all_orders),
            'delivered_orders': len(delivered_orders)
        }
    
    def generate_executive_summary(self, 
                                 comparison_period: Optional[pd.DataFrame] = None) -> Dict:
        """
        Generate an executive summary with key metrics.
        
        Args:
            comparison_period (pd.DataFrame, optional): Data for comparison period
            
        Returns:
            Dict: Executive summary metrics
        """
        revenue_metrics = self.calculate_revenue_metrics(comparison_period)
        product_metrics = self.calculate_product_metrics()
        geographic_metrics = self.calculate_geographic_metrics()
        cx_metrics = self.calculate_customer_experience_metrics()
        operational_metrics = self.calculate_operational_metrics()
        
        # Key insights
        top_category = product_metrics['category_metrics'].index[0]
        top_state = geographic_metrics['state_metrics'].index[0]
        
        summary = {
            'period_summary': {
                'total_revenue': revenue_metrics['total_revenue'],
                'total_orders': revenue_metrics['total_orders'],
                'average_order_value': revenue_metrics['average_order_value'],
                'fulfillment_rate': operational_metrics['fulfillment_rate']
            },
            'growth_metrics': {
                'revenue_growth': revenue_metrics.get('revenue_growth', 0),
                'order_growth': revenue_metrics.get('order_growth', 0),
                'aov_growth': revenue_metrics.get('aov_growth', 0)
            },
            'top_performers': {
                'top_category': top_category,
                'top_category_revenue': product_metrics['category_metrics'].loc[top_category, 'total_revenue'],
                'top_state': top_state,
                'top_state_revenue': geographic_metrics['state_metrics'].loc[top_state, 'total_revenue']
            },
            'customer_experience': {
                'avg_delivery_days': cx_metrics['delivery_metrics']['avg_delivery_days'],
                'avg_review_score': cx_metrics['review_metrics']['avg_review_score'],
                'review_rate': cx_metrics['review_metrics']['review_rate']
            },
            'operational_health': {
                'fulfillment_rate': operational_metrics['fulfillment_rate'],
                'cancellation_rate': operational_metrics['cancellation_rate'],
                'return_rate': operational_metrics['return_rate']
            }
        }
        
        return summary


def calculate_period_comparison(current_data: pd.DataFrame, 
                              previous_data: pd.DataFrame) -> Dict:
    """
    Calculate comparison metrics between two periods.
    
    Args:
        current_data (pd.DataFrame): Current period data
        previous_data (pd.DataFrame): Previous period data
        
    Returns:
        Dict: Comparison metrics
    """
    current_calc = BusinessMetricsCalculator(current_data)
    previous_calc = BusinessMetricsCalculator(previous_data)
    
    current_metrics = current_calc.calculate_revenue_metrics()
    previous_metrics = previous_calc.calculate_revenue_metrics()
    
    comparison = {
        'revenue_change': current_metrics['total_revenue'] - previous_metrics['total_revenue'],
        'revenue_growth_pct': (
            (current_metrics['total_revenue'] - previous_metrics['total_revenue']) / 
            previous_metrics['total_revenue'] * 100
            if previous_metrics['total_revenue'] > 0 else 0
        ),
        'order_change': current_metrics['total_orders'] - previous_metrics['total_orders'],
        'order_growth_pct': (
            (current_metrics['total_orders'] - previous_metrics['total_orders']) / 
            previous_metrics['total_orders'] * 100
            if previous_metrics['total_orders'] > 0 else 0
        ),
        'aov_change': current_metrics['average_order_value'] - previous_metrics['average_order_value'],
        'aov_growth_pct': (
            (current_metrics['average_order_value'] - previous_metrics['average_order_value']) / 
            previous_metrics['average_order_value'] * 100
            if previous_metrics['average_order_value'] > 0 else 0
        )
    }
    
    return comparison