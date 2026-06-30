import os
from dotenv import load_dotenv

load_dotenv()

# Database Configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'sales_db'),
    'port': int(os.getenv('DB_PORT', 3306)),
}

# Data Configuration
DATA_ROWS = int(os.getenv('DATA_ROWS', 50000))
RANDOM_SEED = 42

# File Paths
RAW_DATA_PATH = 'data/raw/sales_data.csv'
PROCESSED_DATA_PATH = 'data/processed/sales_data_cleaned.csv'
EXCEL_OUTPUT_PATH = 'output/excel/sales_report.xlsx'

# ETL Configuration
DATA_INCONSISTENCY_TARGET = 0.30  # 30% reduction goal