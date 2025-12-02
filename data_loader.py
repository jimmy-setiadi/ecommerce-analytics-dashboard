"""
Data Loading and Processing Module for E-commerce Analysis

This module handles loading, cleaning, and preprocessing of e-commerce data
from multiple CSV files and provides a unified interface for analysis.
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional
from datetime import datetime


class EcommerceDataLoader:
    """
    A class to handle loading and preprocessing of e-commerce data.
    
    This class provides methods to load data from CSV files, clean and transform
    the data, and prepare it for business metrics analysis.
    """
    
    def __init__(self, data_path: str = 'ecommerce_data/'):
        """
        Initialize the data loader with the path to data files.
        
        Args:
            data_path (str): Path to the directory containing CSV files
        """
        self.data_path = data_path
        self.raw_data = {}
        self.processed_data = {}
        
    def load_raw_data(self) -> Dict[str, pd.DataFrame]:
        """
        Load all CSV files into pandas DataFrames.
        
        Returns:
            Dict[str, pd.DataFrame]: Dictionary containing all loaded datasets
        """
        file_mapping = {
            'orders': 'orders_dataset.csv',
            'order_items': 'order_items_dataset.csv',
            'products': 'products_dataset.csv',
            'customers': 'customers_dataset.csv',
            'reviews': 'order_reviews_dataset.csv',
            'payments': 'order_payments_dataset.csv'
        }
        
        for key, filename in file_mapping.items():
            try:
                self.raw_data[key] = pd.read_csv(f"{self.data_path}{filename}")
                print(f"Loaded {key}: {len(self.raw_data[key])} records")
            except Exception as e:
                print(f"Error loading {filename}: {str(e)}")
                raise Exception(f"Failed to load required file: {filename}")
                
        return self.raw_data
    
    def clean_and_transform_data(self) -> Dict[str, pd.DataFrame]:
        """
        Clean and transform the raw data for analysis.
        
        Returns:
            Dict[str, pd.DataFrame]: Dictionary containing cleaned datasets
        """
        # Clean orders data
        if 'orders' in self.raw_data:
            orders = self.raw_data['orders'].copy()
            
            # Convert timestamp columns to datetime
            timestamp_cols = [
                'order_purchase_timestamp', 'order_approved_at',
                'order_delivered_carrier_date', 'order_delivered_customer_date',
                'order_estimated_delivery_date'
            ]
            
            for col in timestamp_cols:
                if col in orders.columns:
                    orders[col] = pd.to_datetime(orders[col], errors='coerce')
            
            # Extract date components for analysis
            orders['order_year'] = orders['order_purchase_timestamp'].dt.year
            orders['order_month'] = orders['order_purchase_timestamp'].dt.month
            orders['order_date'] = orders['order_purchase_timestamp'].dt.date
            
            # Calculate delivery time in days
            orders['delivery_days'] = (
                orders['order_delivered_customer_date'] - 
                orders['order_purchase_timestamp']
            ).dt.days
            
            self.processed_data['orders'] = orders
        
        # Clean order items data
        if 'order_items' in self.raw_data:
            order_items = self.raw_data['order_items'].copy()
            
            # Convert shipping limit date
            if 'shipping_limit_date' in order_items.columns:
                order_items['shipping_limit_date'] = pd.to_datetime(
                    order_items['shipping_limit_date'], errors='coerce'
                )
            
            # Calculate total item value (price + freight)
            order_items['total_item_value'] = (
                order_items['price'] + order_items['freight_value']
            )
            
            self.processed_data['order_items'] = order_items
        
        # Clean products data
        if 'products' in self.raw_data:
            products = self.raw_data['products'].copy()
            
            # Clean category names (replace underscores with spaces, title case)
            if 'product_category_name' in products.columns:
                products['category_clean'] = (
                    products['product_category_name']
                    .str.replace('_', ' ')
                    .str.title()
                )
            
            self.processed_data['products'] = products
        
        # Clean customers data
        if 'customers' in self.raw_data:
            customers = self.raw_data['customers'].copy()
            self.processed_data['customers'] = customers
        
        # Clean reviews data
        if 'reviews' in self.raw_data:
            reviews = self.raw_data['reviews'].copy()
            
            # Convert review dates
            if 'review_creation_date' in reviews.columns:
                reviews['review_creation_date'] = pd.to_datetime(
                    reviews['review_creation_date'], errors='coerce'
                )
            
            if 'review_answer_timestamp' in reviews.columns:
                reviews['review_answer_timestamp'] = pd.to_datetime(
                    reviews['review_answer_timestamp'], errors='coerce'
                )
            
            self.processed_data['reviews'] = reviews
        
        # Clean payments data
        if 'payments' in self.raw_data:
            payments = self.raw_data['payments'].copy()
            self.processed_data['payments'] = payments
        
        return self.processed_data
    
    def create_master_dataset(self) -> pd.DataFrame:
        """
        Create a master dataset by joining all relevant tables.
        
        Returns:
            pd.DataFrame: Master dataset with all joined information
        """
        if not self.processed_data:
            self.clean_and_transform_data()
        
        # Start with orders and order_items
        master_df = pd.merge(
            self.processed_data['orders'],
            self.processed_data['order_items'],
            on='order_id',
            how='inner'
        )
        
        # Add product information
        if 'products' in self.processed_data:
            master_df = pd.merge(
                master_df,
                self.processed_data['products'],
                on='product_id',
                how='left'
            )
        
        # Add customer information
        if 'customers' in self.processed_data:
            master_df = pd.merge(
                master_df,
                self.processed_data['customers'],
                on='customer_id',
                how='left'
            )
        
        # Add review information
        if 'reviews' in self.processed_data:
            master_df = pd.merge(
                master_df,
                self.processed_data['reviews'][['order_id', 'review_score']],
                on='order_id',
                how='left'
            )
        
        return master_df
    
    def filter_data_by_date(self, 
                           df: pd.DataFrame, 
                           start_date: Optional[str] = None,
                           end_date: Optional[str] = None,
                           year: Optional[int] = None,
                           month: Optional[int] = None) -> pd.DataFrame:
        """
        Filter dataset by date range or specific year/month.
        
        Args:
            df (pd.DataFrame): Dataset to filter
            start_date (str, optional): Start date in 'YYYY-MM-DD' format
            end_date (str, optional): End date in 'YYYY-MM-DD' format
            year (int, optional): Specific year to filter
            month (int, optional): Specific month to filter (requires year)
            
        Returns:
            pd.DataFrame: Filtered dataset
        """
        filtered_df = df.copy()
        
        # Filter by specific year and month
        if year is not None:
            filtered_df = filtered_df[filtered_df['order_year'] == year]
            
            if month is not None:
                filtered_df = filtered_df[filtered_df['order_month'] == month]
        
        # Filter by date range
        elif start_date is not None or end_date is not None:
            if start_date:
                start_date = pd.to_datetime(start_date)
                filtered_df = filtered_df[
                    filtered_df['order_purchase_timestamp'] >= start_date
                ]
            
            if end_date:
                end_date = pd.to_datetime(end_date)
                filtered_df = filtered_df[
                    filtered_df['order_purchase_timestamp'] <= end_date
                ]
        
        return filtered_df
    
    def get_data_summary(self) -> Dict[str, Dict]:
        """
        Get summary statistics for all loaded datasets.
        
        Returns:
            Dict[str, Dict]: Summary information for each dataset
        """
        summary = {}
        
        for name, df in self.processed_data.items():
            summary[name] = {
                'rows': len(df),
                'columns': len(df.columns),
                'memory_usage': f"{df.memory_usage(deep=True).sum() / 1024**2:.2f} MB",
                'missing_values': df.isnull().sum().sum(),
                'date_range': None
            }
            
            # Add date range for datasets with timestamps
            if name == 'orders' and 'order_purchase_timestamp' in df.columns:
                min_date = df['order_purchase_timestamp'].min()
                max_date = df['order_purchase_timestamp'].max()
                summary[name]['date_range'] = f"{min_date.date()} to {max_date.date()}"
        
        return summary


def load_and_prepare_data(data_path: str = 'ecommerce_data/', 
                         year: Optional[int] = None,
                         month: Optional[int] = None) -> Tuple[pd.DataFrame, EcommerceDataLoader]:
    """
    Convenience function to load and prepare data for analysis.
    
    Args:
        data_path (str): Path to data directory
        year (int, optional): Filter data for specific year
        month (int, optional): Filter data for specific month
        
    Returns:
        Tuple[pd.DataFrame, EcommerceDataLoader]: Master dataset and loader instance
    """
    loader = EcommerceDataLoader(data_path)
    
    # Load and process data
    loader.load_raw_data()
    loader.clean_and_transform_data()
    
    # Create master dataset
    master_df = loader.create_master_dataset()
    
    # Filter by date if specified
    if year is not None or month is not None:
        master_df = loader.filter_data_by_date(master_df, year=year, month=month)
    
    return master_df, loader