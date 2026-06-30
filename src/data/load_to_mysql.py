"""
Load cleaned sales data to MySQL database
"""

import pandas as pd
from src.data.db_connection import DatabaseConnection
from config.logger import logger
from config.config import RAW_DATA_PATH, PROCESSED_DATA_PATH

def load_raw_data_to_mysql():
    """Load raw data from CSV to MySQL"""
    try:
        logger.info("📥 Loading raw data from CSV...")
        df = pd.read_csv(RAW_DATA_PATH)
        
        with DatabaseConnection() as db:
            db.insert_data('sales', df)
            logger.info(f"✓ Loaded {len(df)} rows to MySQL")
            
            # Verify load
            cursor = db.connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM sales")
            count = cursor.fetchone()[0]
            logger.info(f"✓ Verification: {count} rows in database")
            cursor.close()
            
    except Exception as e:
        logger.error(f"✗ Error loading data: {e}")
        raise

def load_processed_data_to_mysql():
    """Load cleaned data to MySQL"""
    try:
        logger.info("📥 Loading processed data from CSV...")
        df = pd.read_csv(PROCESSED_DATA_PATH)
        
        with DatabaseConnection() as db:
            # Drop existing table and reload
            cursor = db.connection.cursor()
            cursor.execute("DROP TABLE IF EXISTS sales_cleaned")
            cursor.close()
            
            db.insert_data('sales_cleaned', df)
            logger.info(f"✓ Loaded {len(df)} cleaned rows to MySQL")
            
    except Exception as e:
        logger.error(f"✗ Error loading processed data: {e}")
        raise

if __name__ == "__main__":
    load_raw_data_to_mysql()