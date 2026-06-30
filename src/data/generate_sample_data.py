"""
Generate 50,000 rows of synthetic sales data using Faker library
Realistic data for retail sales dashboard
"""

import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
from config.config import DATA_ROWS, RANDOM_SEED
from config.logger import logger

fake = Faker()
np.random.seed(RANDOM_SEED)
Faker.seed(RANDOM_SEED)

class SalesDataGenerator:
    """Generate realistic sales data for dashboard"""
    
    def __init__(self, num_records=50000):
        self.num_records = num_records
        self.categories = ['Electronics', 'Clothing', 'Home & Garden', 'Sports', 'Beauty']
        self.regions = ['North', 'South', 'East', 'West', 'Central']
        self.payment_methods = ['Credit Card', 'Debit Card', 'UPI', 'Cash', 'Digital Wallet']
    
    def generate_data(self):
        """Generate complete sales dataset"""
        logger.info(f"📊 Generating {self.num_records} synthetic sales records...")
        
        data = {
            'OrderID': [f'ORD{str(i).zfill(6)}' for i in range(1, self.num_records + 1)],
            'OrderDate': self._generate_dates(),
            'CustomerID': [f'CUST{str(np.random.randint(1000, 9999))}' for _ in range(self.num_records)],
            'CustomerName': [fake.name() for _ in range(self.num_records)],
            'Email': [fake.email() for _ in range(self.num_records)],
            'Phone': [fake.phone_number() for _ in range(self.num_records)],
            'Region': np.random.choice(self.regions, self.num_records),
            'Category': np.random.choice(self.categories, self.num_records),
            'ProductName': [fake.word().title() for _ in range(self.num_records)],
            'Quantity': np.random.randint(1, 20, self.num_records),
            'UnitPrice': np.random.uniform(10, 500, self.num_records),
            'Discount': np.random.choice([0, 0.05, 0.10, 0.15, 0.20], self.num_records),
            'PaymentMethod': np.random.choice(self.payment_methods, self.num_records),
            'OrderStatus': np.random.choice(['Completed', 'Pending', 'Cancelled', 'Returned'], self.num_records, p=[0.75, 0.15, 0.05, 0.05]),
        }
        
        df = pd.DataFrame(data)
        
        # Calculate derived columns
        df['TotalAmount'] = df['Quantity'] * df['UnitPrice']
        df['DiscountAmount'] = df['TotalAmount'] * df['Discount']
        df['Revenue'] = df['TotalAmount'] - df['DiscountAmount']
        
        # Add some intentional data quality issues (for realistic cleaning scenario)
        df = self._introduce_quality_issues(df)
        
        logger.info(f"✓ Generated {len(df)} records with data quality issues")
        return df
    
    def _generate_dates(self):
        """Generate dates over last 12 months"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        dates = [start_date + timedelta(days=np.random.randint(0, 365)) for _ in range(self.num_records)]
        return dates
    
    def _introduce_quality_issues(self, df):
        """Introduce realistic data quality issues (~30% inconsistency)"""
        df_copy = df.copy()
        
        # Missing values (~5% of records)
        missing_indices = np.random.choice(len(df_copy), int(len(df_copy) * 0.05), replace=False)
        df_copy.loc[missing_indices, 'Email'] = np.nan
        
        # Duplicate orders (~2%)
        duplicate_indices = np.random.choice(len(df_copy), int(len(df_copy) * 0.02), replace=False)
        duplicates = df_copy.iloc[duplicate_indices].copy()
        df_copy = pd.concat([df_copy, duplicates], ignore_index=True)
        
        # Invalid prices (~3%)
        invalid_price_indices = np.random.choice(len(df_copy), int(len(df_copy) * 0.03), replace=False)
        df_copy.loc[invalid_price_indices, 'UnitPrice'] = -np.abs(np.random.uniform(1, 100, len(invalid_price_indices)))
        
        # Whitespace in categories (~5%)
        whitespace_indices = np.random.choice(len(df_copy), int(len(df_copy) * 0.05), replace=False)
        df_copy.loc[whitespace_indices, 'Region'] = df_copy.loc[whitespace_indices, 'Region'].str + '  '
        
        # Type inconsistencies in Quantity (~2%)
        quantity_indices = np.random.choice(len(df_copy), int(len(df_copy) * 0.02), replace=False)
        df_copy.loc[quantity_indices, 'Quantity'] = df_copy.loc[quantity_indices, 'Quantity'].astype(str)
        
        logger.info("⚠️  Introduced data quality issues: missing values, duplicates, invalid prices, whitespace")
        return df_copy
    
    def save_csv(self, filepath):
        """Generate data and save to CSV"""
        df = self.generate_data()
        df.to_csv(filepath, index=False)
        logger.info(f"✓ Data saved to {filepath}")
        return df

# Run generator
if __name__ == "__main__":
    generator = SalesDataGenerator(num_records=DATA_ROWS)
    df = generator.generate_data()
    generator.save_csv('data/raw/sales_data.csv')
    print(f"\n{'='*60}")
    print(f"Dataset Shape: {df.shape}")
    print(f"{'='*60}")
    print(df.head(10))
    print(f"\n{'='*60}")
    print(f"Missing Values:\n{df.isnull().sum()}")
    print(f"{'='*60}")