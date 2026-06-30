import mysql.connector
from config.config import DB_CONFIG
from config.logger import logger
from sqlalchemy import create_engine
import pandas as pd

class DatabaseConnection:
    """Handle MySQL database connections and operations"""
    
    def __init__(self):
        self.config = DB_CONFIG
        self.connection = None
        self.engine = None
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(**self.config)
            logger.info(f"✓ Connected to MySQL: {self.config['database']}")
        except mysql.connector.Error as err:
            logger.error(f"✗ Database connection error: {err}")
            raise
    
    def create_sqlalchemy_engine(self):
        """Create SQLAlchemy engine for pandas integration"""
        try:
            connection_string = (
                f"mysql+pymysql://{self.config['user']}:{self.config['password']}"
                f"@{self.config['host']}:{self.config['port']}/{self.config['database']}"
            )
            self.engine = create_engine(connection_string)
            logger.info("✓ SQLAlchemy engine created")
            return self.engine
        except Exception as err:
            logger.error(f"✗ SQLAlchemy engine error: {err}")
            raise
    
    def execute_query(self, query):
        """Execute SQL query and return results"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            logger.info(f"✓ Query executed: {query[:50]}...")
            return results
        except mysql.connector.Error as err:
            logger.error(f"✗ Query execution error: {err}")
            raise
    
    def insert_data(self, table_name, dataframe):
        """Insert pandas DataFrame into database"""
        try:
            dataframe.to_sql(table_name, con=self.engine, if_exists='replace', index=False)
            logger.info(f"✓ Inserted {len(dataframe)} rows into {table_name}")
        except Exception as err:
            logger.error(f"✗ Data insertion error: {err}")
            raise
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("✓ Database connection closed")
    
    def __enter__(self):
        self.connect()
        self.create_sqlalchemy_engine()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()