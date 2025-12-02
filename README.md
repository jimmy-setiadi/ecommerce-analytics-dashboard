# E-commerce Business Analytics - Refactored Analysis

This repository contains a comprehensive, refactored e-commerce business analytics solution with improved code structure, documentation, and interactive dashboard capabilities.

## 📁 Project Structure

```
refactored/
├── data_loader.py              # Data loading and preprocessing module
├── business_metrics.py         # Business metrics calculation module
├── EDA_Refactored.ipynb       # Comprehensive analysis notebook
├── dashboard.py               # Interactive Streamlit dashboard
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## 🚀 Quick Start

### 1. Environment Setup

Create and activate a virtual environment:
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Data Requirements

Ensure your data files are located in `../ecommerce_data/` directory:
- `orders_dataset.csv`
- `order_items_dataset.csv`
- `products_dataset.csv`
- `customers_dataset.csv`
- `order_reviews_dataset.csv`
- `order_payments_dataset.csv`

## 📊 Usage Guide

### Jupyter Notebook Analysis

1. **Launch Jupyter**:
   ```bash
   jupyter notebook EDA_Refactored.ipynb
   ```

2. **Configure Analysis Parameters**:
   - Modify `ANALYSIS_YEAR` and `COMPARISON_YEAR` variables
   - Adjust `DATA_PATH` if your data is in a different location

3. **Run Analysis**:
   - Execute all cells to generate comprehensive business insights
   - The notebook is structured with clear sections and documentation

### Interactive Dashboard

1. **Launch Dashboard**:
   ```bash
   streamlit run dashboard.py
   ```

2. **Use Dashboard Features**:
   - Select date ranges using the date picker
   - View real-time KPI updates
   - Explore interactive visualizations
   - Analyze geographic performance with the US map

## 🔧 Module Documentation

### data_loader.py

**EcommerceDataLoader Class**
- `load_raw_data()`: Load CSV files into pandas DataFrames
- `clean_and_transform_data()`: Clean and preprocess data
- `create_master_dataset()`: Join all datasets into master table
- `filter_data_by_date()`: Filter data by date ranges or specific periods
- `get_data_summary()`: Generate data quality summaries

**Key Functions**
- `load_and_prepare_data()`: Convenience function for quick data loading

### business_metrics.py

**BusinessMetricsCalculator Class**
- `calculate_revenue_metrics()`: Revenue analysis and growth metrics
- `calculate_product_metrics()`: Product category performance
- `calculate_geographic_metrics()`: Geographic distribution analysis
- `calculate_customer_experience_metrics()`: Delivery and satisfaction metrics
- `calculate_operational_metrics()`: Order fulfillment and operational KPIs
- `generate_executive_summary()`: High-level business summary

**Key Functions**
- `calculate_period_comparison()`: Compare metrics between periods

## 📈 Key Features

### Configurable Analysis Framework
- **Flexible Date Filtering**: Analyze any time period or compare different periods
- **Modular Design**: Reusable components for different analysis scenarios
- **Scalable Architecture**: Easy to extend with new metrics and visualizations

### Comprehensive Business Metrics
- **Revenue Analysis**: Total revenue, growth rates, average order value
- **Product Performance**: Category analysis, top performers, market share
- **Geographic Insights**: State and city-level revenue distribution
- **Customer Experience**: Delivery performance, satisfaction scores
- **Operational Health**: Fulfillment rates, cancellation analysis

### Professional Visualizations
- **Interactive Charts**: Plotly-powered visualizations in dashboard
- **Business-Oriented Colors**: Consistent, professional color schemes
- **Clear Formatting**: Currency and number formatting for readability
- **Trend Indicators**: Visual indicators for performance changes

### Dashboard Features
- **Real-time KPIs**: Key performance indicators with trend arrows
- **Interactive Filtering**: Date range selection affects all visualizations
- **Geographic Mapping**: US choropleth map for state-level analysis
- **Responsive Design**: Professional layout that works on different screen sizes

## 🎯 Business Insights Provided

### Revenue Performance
- Year-over-year revenue growth analysis
- Monthly revenue trends and seasonality
- Average order value trends
- Revenue per customer metrics

### Product Analytics
- Top-performing product categories
- Revenue share distribution
- Product portfolio analysis
- Category growth comparisons

### Geographic Analysis
- Revenue distribution by state and city
- Geographic market penetration
- Regional performance comparisons
- Market opportunity identification

### Customer Experience
- Delivery performance metrics
- Customer satisfaction analysis
- Review score distributions
- Satisfaction vs delivery time correlation

### Operational Metrics
- Order fulfillment rates
- Cancellation and return analysis
- Process efficiency indicators
- Operational health monitoring

## 🔄 Customization Guide

### Adding New Metrics

1. **Extend BusinessMetricsCalculator**:
   ```python
   def calculate_custom_metric(self) -> Dict:
       # Your custom calculation logic
       return custom_metrics
   ```

2. **Update Dashboard**:
   - Add new visualization functions
   - Include in main dashboard layout

### Modifying Date Ranges

```python
# In notebook configuration cell
ANALYSIS_YEAR = 2024  # Change to desired year
COMPARISON_YEAR = 2023  # Change comparison period

# For custom date ranges
start_date = "2023-06-01"
end_date = "2023-12-31"
filtered_data = loader.filter_data_by_date(data, start_date=start_date, end_date=end_date)
```

### Adding New Visualizations

```python
def create_custom_chart(data):
    fig = go.Figure()
    # Your chart logic here
    return fig

# Add to dashboard layout
st.plotly_chart(create_custom_chart(data), use_container_width=True)
```

## 🛠️ Technical Requirements

- **Python**: 3.8 or higher
- **Memory**: Minimum 4GB RAM (8GB recommended for large datasets)
- **Storage**: 1GB free space for data and dependencies
- **Browser**: Modern web browser for dashboard (Chrome, Firefox, Safari, Edge)

## 📝 Data Dictionary

### Key Business Terms
- **Revenue**: Total sales from delivered orders only
- **AOV**: Average Order Value per completed transaction
- **Fulfillment Rate**: Percentage of orders successfully delivered
- **Review Score**: Customer satisfaction rating (1-5 scale)
- **Delivery Days**: Time between order placement and delivery

### Data Quality Notes
- Canceled and returned orders are excluded from revenue calculations
- Missing delivery dates are handled gracefully in delivery time analysis
- Geographic analysis uses customer location data
- Review analysis includes only orders with customer feedback

## 🤝 Contributing

To extend this analysis framework:

1. Follow the existing code structure and documentation standards
2. Add comprehensive docstrings to new functions
3. Include error handling for data quality issues
4. Test with different date ranges and data scenarios
5. Update this README with new features

## 📞 Support

For questions or issues:
- Review the comprehensive documentation in the Jupyter notebook
- Check function docstrings for detailed parameter information
- Ensure data files are in the correct format and location
- Verify all dependencies are installed correctly

---

**Last Updated**: January 2025  
**Version**: 1.0.0  
**Compatibility**: Python 3.8+, Pandas 2.0+, Streamlit 1.28+