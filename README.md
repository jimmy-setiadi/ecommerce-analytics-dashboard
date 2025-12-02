# E-commerce Analytics Dashboard

An interactive Streamlit dashboard for comprehensive e-commerce data analysis, featuring real-time KPIs, revenue trends, and customer insights.

## 🚀 Live Demo
**[🔗 Click here to view the live dashboard](https://ecommerce-analytics-dashboard.streamlit.app)**

*Try the interactive features: adjust date ranges, explore different metrics, and analyze business performance in real-time!*

## 📊 Features

- **KPI Overview**: Total revenue, orders, customers, and average order value
- **Revenue Analysis**: Monthly trends with year-over-year comparisons
- **Product Insights**: Top-performing categories and product analysis
- **Geographic Distribution**: Customer and revenue mapping by state
- **Customer Experience**: Satisfaction scores and delivery performance
- **Interactive Filtering**: Date range selection for focused analysis

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **Data Processing**: Pandas, NumPy
- **Visualization**: Plotly
- **Deployment**: Streamlit Community Cloud

## 📁 Project Structure

```
├── dashboard.py              # Main Streamlit application
├── data_loader.py           # Data loading and preprocessing
├── business_metrics.py      # Business logic and calculations
├── EDA_Refactored.ipynb    # Comprehensive data analysis notebook
├── ecommerce_data/         # CSV datasets
└── requirements.txt        # Dependencies
```

## 🔧 Local Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the dashboard: `streamlit run dashboard.py`

## 📈 Data Sources

The dashboard analyzes e-commerce data including:
- Orders and order items
- Product catalog and categories
- Customer information
- Payment records
- Review and rating data

## 🎯 Key Insights

The dashboard provides actionable business intelligence through:
- Revenue trend analysis with period-over-period comparisons
- Product category performance rankings
- Geographic sales distribution across states
- Customer satisfaction correlation with delivery performance
- Operational metrics for business optimization

---
*Built with modern data science practices and deployed on Streamlit Community Cloud*