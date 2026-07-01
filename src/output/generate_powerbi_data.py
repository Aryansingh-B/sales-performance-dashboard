"""
Generate aggregated CSVs optimized for Power BI import
Faster loading and cleaner data model
"""

import pandas as pd
from datetime import datetime
from config.logger import logger
from config.config import PROCESSED_DATA_PATH
import os

class PowerBIDataExporter:
    """Export data optimized for Power BI"""
    
    def __init__(self, data_path=PROCESSED_DATA_PATH):
        self.df = pd.read_csv(data_path)
        self.df['OrderDate'] = pd.to_datetime(self.df['OrderDate'])
        self.export_dir = 'output/powerbi_data'
        os.makedirs(self.export_dir, exist_ok=True)
        logger.info(f"📊 Initializing Power BI Data Exporter...")
    
    def export_all(self):
        """Export all datasets for Power BI"""
        logger.info("\n" + "="*60)
        logger.info("POWER BI DATA EXPORT")
        logger.info("="*60)
        
        self._export_fact_sales()
        self._export_date_dimension()
        self._export_region_dimension()
        self._export_category_dimension()
        self._export_aggregated_metrics()
        
        logger.info("\n✅ Power BI data export complete!")
    
    def _export_fact_sales(self):
        """Export main sales fact table"""
        logger.info("\n📤 Exporting Sales Fact Table...")
        
        # Select relevant columns
        fact_sales = self.df[[
            'OrderID', 'OrderDate', 'CustomerID', 'Region', 'Category',
            'ProductName', 'Quantity', 'UnitPrice', 'Discount',
            'TotalAmount', 'DiscountAmount', 'Revenue', 'OrderStatus',
            'PaymentMethod'
        ]].copy()
        
        # Sort by date
        fact_sales = fact_sales.sort_values('OrderDate')
        
        path = f'{self.export_dir}/FactSales.csv'
        fact_sales.to_csv(path, index=False)
        logger.info(f"  ✓ Saved: {path} ({len(fact_sales)} rows)")
    
    def _export_date_dimension(self):
        """Export date dimension table"""
        logger.info("\n📅 Exporting Date Dimension...")
        
        # Create date range
        date_range = pd.date_range(
            start=self.df['OrderDate'].min(),
            end=self.df['OrderDate'].max(),
            freq='D'
        )
        
        date_dim = pd.DataFrame({
            'DateKey': date_range.strftime('%Y%m%d').astype(int),
            'Date': date_range,
            'Year': date_range.year,
            'Quarter': date_range.quarter,
            'Month': date_range.month,
            'MonthName': date_range.strftime('%B'),
            'Week': date_range.isocalendar().week,
            'DayOfWeek': date_range.day_name(),
            'IsWeekend': date_range.dayofweek.isin([5, 6]).astype(int)
        })
        
        path = f'{self.export_dir}/DimDate.csv'
        date_dim.to_csv(path, index=False)
        logger.info(f"  ✓ Saved: {path} ({len(date_dim)} rows)")
    
    def _export_region_dimension(self):
        """Export region dimension table"""
        logger.info("\n🗺️  Exporting Region Dimension...")
        
        region_dim = pd.DataFrame({
            'RegionKey': range(1, len(self.df['Region'].unique()) + 1),
            'Region': self.df['Region'].unique()
        }).sort_values('Region').reset_index(drop=True)
        
        path = f'{self.export_dir}/DimRegion.csv'
        region_dim.to_csv(path, index=False)
        logger.info(f"  ✓ Saved: {path} ({len(region_dim)} rows)")
    
    def _export_category_dimension(self):
        """Export category dimension table"""
        logger.info("\n📂 Exporting Category Dimension...")
        
        category_dim = pd.DataFrame({
            'CategoryKey': range(1, len(self.df['Category'].unique()) + 1),
            'Category': self.df['Category'].unique()
        }).sort_values('Category').reset_index(drop=True)
        
        path = f'{self.export_dir}/DimCategory.csv'
        category_dim.to_csv(path, index=False)
        logger.info(f"  ✓ Saved: {path} ({len(category_dim)} rows)")
    
    def _export_aggregated_metrics(self):
        """Export pre-aggregated metrics for dashboard"""
        logger.info("\n📊 Exporting Aggregated Metrics...")
        
        # Monthly revenue
        monthly = self.df.groupby(self.df['OrderDate'].dt.to_period('M')).agg({
            'Revenue': 'sum',
            'OrderID': 'count',
            'CustomerID': 'nunique',
            'Quantity': 'sum'
        }).round(2)
        monthly.index = monthly.index.to_timestamp()
        monthly_path = f'{self.export_dir}/MetricsMonthly.csv'
        monthly.to_csv(monthly_path)
        logger.info(f"  ✓ Saved: {monthly_path}")
        
        # Regional summary
        regional = self.df.groupby('Region').agg({
            'Revenue': 'sum',
            'OrderID': 'count',
            'CustomerID': 'nunique'
        }).round(2)
        regional_path = f'{self.export_dir}/MetricsRegional.csv'
        regional.to_csv(regional_path)
        logger.info(f"  ✓ Saved: {regional_path}")
        
        # Category summary
        category = self.df.groupby('Category').agg({
            'Revenue': 'sum',
            'Quantity': 'sum',
            'OrderID': 'count'
        }).round(2)
        category_path = f'{self.export_dir}/MetricsCategory.csv'
        category.to_csv(category_path)
        logger.info(f"  ✓ Saved: {category_path}")

# Run exporter
if __name__ == "__main__":
    exporter = PowerBIDataExporter()
    exporter.export_all()