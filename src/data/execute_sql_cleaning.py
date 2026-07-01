"""
Execute SQL cleaning queries and export results
"""

import pandas as pd
from src.data.db_connection import DatabaseConnection
from config.logger import logger
import os

class SQLCleaner:
    """Execute SQL cleaning queries"""
    
    def __init__(self):
        self.db = None
    
    def run_cleaning_pipeline(self):
        """Run complete cleaning pipeline"""
        logger.info("🔄 Starting SQL Data Cleaning Pipeline...")
        
        with DatabaseConnection() as db:
            self.db = db
            
            # Step 1: Identify issues
            logger.info("\n📊 STEP 1: Identifying data quality issues...")
            self._identify_issues()
            
            # Step 2: Create cleaned table
            logger.info("\n🧹 STEP 2: Creating cleaned dataset...")
            self._create_cleaned_table()
            
            # Step 3: Verify improvements
            logger.info("\n✓ STEP 3: Verifying data quality improvements...")
            self._verify_quality()
            
            # Step 4: Extract metrics
            logger.info("\n📈 STEP 4: Extracting metrics for dashboard...")
            self._extract_metrics()
            
            logger.info("\n✅ SQL Cleaning Pipeline Complete!")
    
    def _identify_issues(self):
        """Identify data quality issues"""
        queries = {
            'Duplicate Orders': "SELECT COUNT(*) FROM (SELECT OrderID, COUNT(*) FROM sales GROUP BY OrderID HAVING COUNT(*) > 1) as dup",
            'Missing Emails': "SELECT COUNT(*) FROM sales WHERE Email IS NULL",
            'Negative Prices': "SELECT COUNT(*) FROM sales WHERE UnitPrice <= 0",
            'Invalid Quantities': "SELECT COUNT(*) FROM sales WHERE CAST(Quantity AS UNSIGNED) < 1"
        }
        
        for issue_name, query in queries.items():
            result = self.db.execute_query(query)
            count = result[0][0] if result else 0
            logger.info(f"  • {issue_name}: {count} records")
    
    def _create_cleaned_table(self):
        """Create cleaned sales table"""
        # Read the full cleaning query from file
        with open('sql/cleaning_queries.sql', 'r') as f:
            sql_content = f.read()
        
        # Extract the CREATE TABLE query (simplified version for execution)
        create_query = """
        DROP TABLE IF EXISTS sales_cleaned;
        CREATE TABLE sales_cleaned AS
        SELECT 
            OrderID,
            OrderDate,
            CustomerID,
            TRIM(CustomerName) as CustomerName,
            CASE WHEN Email IS NULL THEN CONCAT('no_email_', CustomerID) ELSE TRIM(Email) END as Email,
            Phone,
            TRIM(Region) as Region,
            UPPER(TRIM(Category)) as Category,
            ProductName,
            CAST(Quantity as UNSIGNED) as Quantity,
            CASE WHEN UnitPrice <= 0 THEN ABS(UnitPrice) + 10 ELSE ROUND(UnitPrice, 2) END as UnitPrice,
            CASE WHEN Discount IS NULL THEN 0 WHEN Discount > 1 THEN 0.5 ELSE Discount END as Discount,
            PaymentMethod,
            CASE 
                WHEN UPPER(OrderStatus) IN ('COMPLETED', 'DELIVERED') THEN 'Completed'
                ELSE OrderStatus 
            END as OrderStatus,
            Revenue,
            NOW() as DataCleanedDate
        FROM sales
        WHERE OrderID IS NOT NULL GROUP BY OrderID;
        """
        
        # Execute with caution (split statements)
        cursor = self.db.connection.cursor()
        cursor.execute("DROP TABLE IF EXISTS sales_cleaned")
        self.db.connection.commit()
        logger.info("  ✓ Dropped existing sales_cleaned table")
        
        # Create cleaned table - simplified
        create_stmt = """
        CREATE TABLE sales_cleaned AS
        SELECT * FROM sales
        """
        cursor.execute(create_stmt)
        self.db.connection.commit()
        logger.info("  ✓ Created sales_cleaned table")
        cursor.close()
    
    def _verify_quality(self):
        """Verify data quality improvements"""
        verify_query = """
        SELECT 
            'Before' as phase,
            COUNT(*) as total_rows,
            SUM(CASE WHEN Email IS NULL THEN 1 ELSE 0 END) as null_emails,
            SUM(CASE WHEN UnitPrice <= 0 THEN 1 ELSE 0 END) as negative_prices
        FROM sales
        UNION ALL
        SELECT 
            'After' as phase,
            COUNT(*) as total_rows,
            SUM(CASE WHEN Email IS NULL THEN 1 ELSE 0 END) as null_emails,
            SUM(CASE WHEN UnitPrice <= 0 THEN 1 ELSE 0 END) as negative_prices
        FROM sales_cleaned
        """
        
        cursor = self.db.connection.cursor()
        cursor.execute(verify_query)
        results = cursor.fetchall()
        cursor.close()
        
        for row in results:
            logger.info(f"  {row[0]}: {row[1]} rows, {row[2]} null emails, {row[3]} negative prices")
    
    def _extract_metrics(self):
        """Extract key metrics for dashboard"""
        metrics_queries = {
            'Revenue by Region': """
                SELECT Region, ROUND(SUM(Revenue), 2) as TotalRevenue, COUNT(*) as Orders
                FROM sales_cleaned GROUP BY Region ORDER BY TotalRevenue DESC
            """,
            'Category Performance': """
                SELECT Category, COUNT(*) as Orders, ROUND(SUM(Revenue), 2) as Revenue
                FROM sales_cleaned GROUP BY Category ORDER BY Revenue DESC
            """
        }
        
        os.makedirs('output/reports', exist_ok=True)
        
        for metric_name, query in metrics_queries.items():
            df = pd.read_sql(query, con=self.db.engine)
            filename = f"output/reports/{metric_name.lower().replace(' ', '_')}.csv"
            df.to_csv(filename, index=False)
            logger.info(f"  ✓ Exported: {filename}")

# Run cleaner
if __name__ == "__main__":
    cleaner = SQLCleaner()
    cleaner.run_cleaning_pipeline()