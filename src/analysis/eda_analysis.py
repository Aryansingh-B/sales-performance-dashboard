"""
Exploratory Data Analysis (EDA) Pipeline
Analyze sales patterns, distributions, and correlations
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from config.logger import logger
from config.config import PROCESSED_DATA_PATH
import os

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 6)
plt.rcParams['font.size'] = 10

class SalesEDA:
    """Comprehensive EDA for sales data"""
    
    def __init__(self, datapath=PROCESSED_DATA_PATH):
        self.df = pd.read_csv(datapath)
        self.figures_dir = 'output/dashboards/eda_figures'
        os.makedirs(self.figures_dir, exist_ok=True)
        logger.info(f"📊 Loaded {len(self.df)} records for EDA")
    
    def run_complete_eda(self):
        """Execute all EDA steps"""
        logger.info("🔍 Starting Exploratory Data Analysis...")
        
        self.data_overview()
        self.distribution_analysis()
        self.categorical_analysis()
        self.time_series_analysis()
        self.correlation_analysis()
        self.business_insights()
        
        logger.info("✅ EDA Complete!")
    
    def data_overview(self):
        """Basic data overview"""
        logger.info("\n📋 DATA OVERVIEW")
        logger.info(f"Shape: {self.df.shape}")
        logger.info(f"Memory Usage: {self.df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        logger.info(f"\nColumn Data Types:\n{self.df.dtypes}")
        logger.info(f"\nMissing Values:\n{self.df.isnull().sum()}")
        logger.info(f"\nBasic Statistics:\n{self.df.describe()}")
    
    def distribution_analysis(self):
        """Analyze distributions"""
        logger.info("\n📊 DISTRIBUTION ANALYSIS")
        
        # Revenue distribution
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        axes[0, 0].hist(self.df['Revenue'], bins=50, color='steelblue', edgecolor='black')
        axes[0, 0].set_title('Revenue Distribution', fontsize=12, fontweight='bold')
        axes[0, 0].set_xlabel('Revenue ($)')
        axes[0, 0].set_ylabel('Frequency')
        
        axes[0, 1].hist(self.df['Quantity'], bins=30, color='orange', edgecolor='black')
        axes[0, 1].set_title('Quantity Distribution', fontsize=12, fontweight='bold')
        axes[0, 1].set_xlabel('Quantity')
        axes[0, 1].set_ylabel('Frequency')
        
        # Box plots
        axes[1, 0].boxplot(self.df['Revenue'], vert=False)
        axes[1, 0].set_title('Revenue Box Plot', fontsize=12, fontweight='bold')
        axes[1, 0].set_xlabel('Revenue ($)')
        
        axes[1, 1].boxplot(self.df['UnitPrice'], vert=False)
        axes[1, 1].set_title('Unit Price Box Plot', fontsize=12, fontweight='bold')
        axes[1, 1].set_xlabel('Unit Price ($)')
        
        plt.tight_layout()
        plt.savefig(f'{self.figures_dir}/01_distribution_analysis.png', dpi=300, bbox_inches='tight')
        logger.info(f"  ✓ Saved: 01_distribution_analysis.png")
        plt.close()
        
        # Statistics
        logger.info(f"  Revenue: Mean=${self.df['Revenue'].mean():.2f}, Median=${self.df['Revenue'].median():.2f}")
        logger.info(f"  Revenue: Skewness={self.df['Revenue'].skew():.2f}, Kurtosis={self.df['Revenue'].kurtosis():.2f}")
        logger.info(f"  Quantity: Mean={self.df['Quantity'].mean():.2f}, Std={self.df['Quantity'].std():.2f}")
    
    def categorical_analysis(self):
        """Analyze categorical variables"""
        logger.info("\n🏷️  CATEGORICAL ANALYSIS")
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # Revenue by Region
        region_revenue = self.df.groupby('Region')['Revenue'].sum().sort_values(ascending=False)
        axes[0, 0].barh(region_revenue.index, region_revenue.values, color='steelblue')
        axes[0, 0].set_title('Revenue by Region', fontsize=12, fontweight='bold')
        axes[0, 0].set_xlabel('Total Revenue ($)')
        for i, v in enumerate(region_revenue.values):
            axes[0, 0].text(v, i, f' ${v:,.0f}', va='center')
        
        # Revenue by Category
        category_revenue = self.df.groupby('Category')['Revenue'].sum().sort_values(ascending=False)
        axes[0, 1].bar(category_revenue.index, category_revenue.values, color='orange', edgecolor='black')
        axes[0, 1].set_title('Revenue by Category', fontsize=12, fontweight='bold')
        axes[0, 1].set_ylabel('Total Revenue ($)')
        axes[0, 1].tick_params(axis='x', rotation=45)
        for i, v in enumerate(category_revenue.values):
            axes[0, 1].text(i, v, f'${v/1000:.0f}K', ha='center', va='bottom')
        
        # Orders by Status
        status_counts = self.df['OrderStatus'].value_counts()
        colors = ['#2ecc71', '#f39c12', '#e74c3c', '#95a5a6']
        axes[1, 0].pie(status_counts.values, labels=status_counts.index, autopct='%1.1f%%',
                       colors=colors, startangle=90)
        axes[1, 0].set_title('Orders by Status', fontsize=12, fontweight='bold')
        
        # Payment Method Distribution
        payment_revenue = self.df.groupby('PaymentMethod')['Revenue'].sum().sort_values(ascending=False)
        axes[1, 1].barh(payment_revenue.index, payment_revenue.values, color='green', edgecolor='black')
        axes[1, 1].set_title('Revenue by Payment Method', fontsize=12, fontweight='bold')
        axes[1, 1].set_xlabel('Total Revenue ($)')
        
        plt.tight_layout()
        plt.savefig(f'{self.figures_dir}/02_categorical_analysis.png', dpi=300, bbox_inches='tight')
        logger.info(f"  ✓ Saved: 02_categorical_analysis.png")
        plt.close()
        
        # Summary statistics
        logger.info(f"\n  Revenue by Region:")
        for region, revenue in region_revenue.items():
            pct = (revenue / region_revenue.sum()) * 100
            logger.info(f"    {region}: ${revenue:,.2f} ({pct:.1f}%)")
        
        logger.info(f"\n  Order Status Distribution:")
        for status, count in status_counts.items():
            pct = (count / status_counts.sum()) * 100
            logger.info(f"    {status}: {count} ({pct:.1f}%)")
    
    def time_series_analysis(self):
        """Analyze trends over time"""
        logger.info("\n📈 TIME SERIES ANALYSIS")
        
        # Convert OrderDate to datetime
        self.df['OrderDate'] = pd.to_datetime(self.df['OrderDate'])
        
        # Daily revenue trend
        daily_revenue = self.df.groupby(self.df['OrderDate'].dt.date)['Revenue'].sum()
        
        # Monthly revenue trend
        monthly_revenue = self.df.groupby(self.df['OrderDate'].dt.to_period('M'))['Revenue'].sum()
        
        fig, axes = plt.subplots(2, 1, figsize=(14, 10))
        
        # Daily trend
        axes[0].plot(daily_revenue.index, daily_revenue.values, linewidth=2, color='steelblue')
        axes[0].fill_between(range(len(daily_revenue)), daily_revenue.values, alpha=0.3, color='steelblue')
        axes[0].set_title('Daily Revenue Trend', fontsize=12, fontweight='bold')
        axes[0].set_ylabel('Revenue ($)')
        axes[0].grid(True, alpha=0.3)
        
        # Monthly trend
        axes[1].plot(range(len(monthly_revenue)), monthly_revenue.values, marker='o', 
                     linewidth=2, markersize=8, color='orange')
        axes[1].set_title('Monthly Revenue Trend', fontsize=12, fontweight='bold')
        axes[1].set_ylabel('Revenue ($)')
        axes[1].set_xlabel('Month')
        axes[1].grid(True, alpha=0.3)
        axes[1].set_xticks(range(len(monthly_revenue)))
        axes[1].set_xticklabels([str(p) for p in monthly_revenue.index], rotation=45)
        
        plt.tight_layout()
        plt.savefig(f'{self.figures_dir}/03_time_series_analysis.png', dpi=300, bbox_inches='tight')
        logger.info(f"  ✓ Saved: 03_time_series_analysis.png")
        plt.close()
        
        # Growth rate
        growth_rate = (monthly_revenue.pct_change() * 100).dropna()
        logger.info(f"\n  Monthly Revenue Growth Rates (%):")
        for period, rate in growth_rate.items():
            logger.info(f"    {period}: {rate:+.2f}%")
    
    def correlation_analysis(self):
        """Analyze correlations"""
        logger.info("\n🔗 CORRELATION ANALYSIS")
        
        # Select numeric columns
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        correlation_matrix = self.df[numeric_cols].corr()
        
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(correlation_matrix, annot=True, fmt='.2f', cmap='coolwarm', 
                    center=0, square=True, ax=ax, cbar_kws={'label': 'Correlation'})
        ax.set_title('Correlation Matrix - Numeric Variables', fontsize=12, fontweight='bold')
        plt.tight_layout()
        plt.savefig(f'{self.figures_dir}/04_correlation_analysis.png', dpi=300, bbox_inches='tight')
        logger.info(f"  ✓ Saved: 04_correlation_analysis.png")
        plt.close()
        
        logger.info(f"\n  Top Correlations with Revenue:")
        revenue_corr = correlation_matrix['Revenue'].sort_values(ascending=False)
        for var, corr in revenue_corr.items():
            if var != 'Revenue':
                logger.info(f"    {var}: {corr:.3f}")
    
    def business_insights(self):
        """Generate business insights"""
        logger.info("\n💡 KEY BUSINESS INSIGHTS")
        
        # Top performing regions
        top_region = self.df.groupby('Region')['Revenue'].sum().idxmax()
        top_region_revenue = self.df.groupby('Region')['Revenue'].sum().max()
        logger.info(f"\n  🏆 Top Region: {top_region} (${top_region_revenue:,.2f})")
        
        # Top performing category
        top_category = self.df.groupby('Category')['Revenue'].sum().idxmax()
        top_category_revenue = self.df.groupby('Category')['Revenue'].sum().max()
        logger.info(f"  🏆 Top Category: {top_category} (${top_category_revenue:,.2f})")
        
        # Highest discount impact
        high_discount = self.df[self.df['Discount'] > 0.15]
        if len(high_discount) > 0:
            discount_impact = high_discount['DiscountAmount'].sum()
            logger.info(f"\n  💰 Revenue Loss from Heavy Discounts (>15%): ${discount_impact:,.2f}")
            logger.info(f"     Affected Orders: {len(high_discount)}")
        
        # Order status analysis
        completed_revenue_pct = (self.df[self.df['OrderStatus'] == 'Completed']['Revenue'].sum() / 
                                self.df['Revenue'].sum()) * 100
        logger.info(f"\n  📊 Completed Orders Revenue: {completed_revenue_pct:.1f}%")
        
        # Customer concentration
        customer_revenue = self.df.groupby('CustomerID')['Revenue'].sum()
        top_10_pct = (customer_revenue.nlargest(10).sum() / customer_revenue.sum()) * 100
        logger.info(f"  👥 Top 10 Customers: {top_10_pct:.1f}% of total revenue")
        
        # Average order value
        aov = self.df['Revenue'].sum() / len(self.df)
        logger.info(f"\n  💵 Average Order Value: ${aov:.2f}")
        
        # Payment method preferences
        preferred_payment = self.df['PaymentMethod'].value_counts().idxmax()
        preferred_pct = (self.df['PaymentMethod'].value_counts().max() / len(self.df)) * 100
        logger.info(f"  💳 Preferred Payment Method: {preferred_payment} ({preferred_pct:.1f}%)")

# Run EDA
if __name__ == "__main__":
    eda = SalesEDA()
    eda.run_complete_eda()