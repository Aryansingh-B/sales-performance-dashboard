-- ============================================
-- STEP 1: IDENTIFY DATA QUALITY ISSUES
-- ============================================

-- Find duplicate orders
SELECT OrderID, COUNT(*) as duplicate_count
FROM sales
GROUP BY OrderID
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC;

-- Find missing emails
SELECT COUNT(*) as missing_emails
FROM sales
WHERE Email IS NULL OR Email = '';

-- Find negative or zero prices
SELECT COUNT(*) as invalid_prices
FROM sales
WHERE UnitPrice <= 0 OR Revenue <= 0;

-- Find whitespace in regions
SELECT DISTINCT Region, LENGTH(Region) as region_length
FROM sales
WHERE Region LIKE '%  %' OR TRIM(Region) != Region;

-- Check for invalid order dates (future dates or too old)
SELECT COUNT(*) as invalid_dates
FROM sales
WHERE OrderDate > NOW() OR OrderDate < DATE_SUB(NOW(), INTERVAL 2 YEAR);

-- ============================================
-- STEP 2: CREATE CLEANED TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS sales_cleaned AS
SELECT 
    -- Remove duplicates using ROW_NUMBER()
    OrderID,
    
    -- Fix date issues
    CASE 
        WHEN OrderDate IS NULL THEN NOW()
        WHEN OrderDate > NOW() THEN NOW()
        WHEN OrderDate < DATE_SUB(NOW(), INTERVAL 2 YEAR) THEN NOW()
        ELSE OrderDate
    END as OrderDate,
    
    CustomerID,
    
    -- Trim customer names
    TRIM(CustomerName) as CustomerName,
    
    -- Handle missing emails
    CASE 
        WHEN Email IS NULL OR Email = '' THEN CONCAT('no_email_', CustomerID, '@unknown.com')
        ELSE TRIM(Email)
    END as Email,
    
    Phone,
    
    -- Fix region whitespace
    TRIM(Region) as Region,
    
    -- Standardize category
    UPPER(TRIM(Category)) as Category,
    
    ProductName,
    
    -- Ensure Quantity is integer
    CAST(Quantity as UNSIGNED) as Quantity,
    
    -- Fix negative prices
    CASE 
        WHEN UnitPrice <= 0 THEN ABS(UnitPrice) + 10
        ELSE ROUND(UnitPrice, 2)
    END as UnitPrice,
    
    -- Validate discount (0-1 range)
    CASE 
        WHEN Discount IS NULL THEN 0
        WHEN Discount > 1 THEN 0.5
        WHEN Discount < 0 THEN 0
        ELSE Discount
    END as Discount,
    
    PaymentMethod,
    
    -- Standardize order status
    CASE 
        WHEN UPPER(OrderStatus) IN ('COMPLETED', 'DELIVERED') THEN 'Completed'
        WHEN UPPER(OrderStatus) = 'PENDING' THEN 'Pending'
        WHEN UPPER(OrderStatus) IN ('CANCELLED', 'CANCEL') THEN 'Cancelled'
        WHEN UPPER(OrderStatus) = 'RETURNED' THEN 'Returned'
        ELSE 'Unknown'
    END as OrderStatus,
    
    -- Recalculate amounts
    ROUND(CAST(Quantity as UNSIGNED) * 
        CASE WHEN UnitPrice <= 0 THEN ABS(UnitPrice) + 10 ELSE UnitPrice END, 2) as TotalAmount,
    
    ROUND(ROUND(CAST(Quantity as UNSIGNED) * 
        CASE WHEN UnitPrice <= 0 THEN ABS(UnitPrice) + 10 ELSE UnitPrice END, 2) * 
        CASE WHEN Discount IS NULL THEN 0 WHEN Discount > 1 THEN 0.5 
        WHEN Discount < 0 THEN 0 ELSE Discount END, 2) as DiscountAmount,
    
    -- Revenue = Total - Discount
    ROUND(ROUND(CAST(Quantity as UNSIGNED) * 
        CASE WHEN UnitPrice <= 0 THEN ABS(UnitPrice) + 10 ELSE UnitPrice END, 2) * 
        (1 - CASE WHEN Discount IS NULL THEN 0 WHEN Discount > 1 THEN 0.5 
        WHEN Discount < 0 THEN 0 ELSE Discount END), 2) as Revenue,
    
    NOW() as DataCleanedDate,
    'Cleaned' as DataQualityStatus
    
FROM sales
WHERE 
    -- Remove completely invalid records
    OrderID IS NOT NULL
    AND CustomerID IS NOT NULL
    AND Region IS NOT NULL
    AND (OrderID, OrderDate) NOT IN (
        SELECT OrderID, OrderDate
        FROM sales
        WHERE ROW_NUMBER() OVER (PARTITION BY OrderID ORDER BY OrderDate DESC) > 1
    )
GROUP BY OrderID  -- Handle duplicates
ORDER BY OrderDate DESC;

-- ============================================
-- STEP 3: VERIFY DATA QUALITY IMPROVEMENT
-- ============================================

-- Missing values after cleaning
SELECT 
    'sales' as table_name,
    SUM(CASE WHEN OrderID IS NULL THEN 1 ELSE 0 END) as null_orderid,
    SUM(CASE WHEN Email IS NULL THEN 1 ELSE 0 END) as null_email,
    SUM(CASE WHEN UnitPrice <= 0 THEN 1 ELSE 0 END) as invalid_price,
    SUM(CASE WHEN Discount NOT BETWEEN 0 AND 1 THEN 1 ELSE 0 END) as invalid_discount,
    COUNT(*) as total_records
FROM sales_cleaned;

-- Duplicate reduction metrics
SELECT 
    'Duplicates Removed' as metric,
    (SELECT COUNT(*) FROM sales) - (SELECT COUNT(*) FROM sales_cleaned) as count;

-- Data quality score
SELECT 
    ROUND(
        ((SELECT COUNT(*) FROM sales_cleaned WHERE Email NOT LIKE '%unknown%') / 
         (SELECT COUNT(*) FROM sales_cleaned)) * 100, 2
    ) as email_quality_percent,
    ROUND(
        ((SELECT COUNT(*) FROM sales_cleaned WHERE UnitPrice > 0) / 
         (SELECT COUNT(*) FROM sales_cleaned)) * 100, 2
    ) as price_quality_percent,
    ROUND(
        ((SELECT COUNT(*) FROM sales_cleaned WHERE Discount BETWEEN 0 AND 1) / 
         (SELECT COUNT(*) FROM sales_cleaned)) * 100, 2
    ) as discount_quality_percent;

-- ============================================
-- STEP 4: EXTRACT METRICS FOR DASHBOARD
-- ============================================

-- Revenue by Region
SELECT 
    Region,
    YEAR(OrderDate) as Year,
    MONTH(OrderDate) as Month,
    SUM(Revenue) as TotalRevenue,
    COUNT(DISTINCT OrderID) as TotalOrders,
    COUNT(DISTINCT CustomerID) as UniqueCustomers,
    ROUND(SUM(Revenue) / COUNT(DISTINCT OrderID), 2) as AvgOrderValue
FROM sales_cleaned
GROUP BY Region, YEAR(OrderDate), MONTH(OrderDate)
ORDER BY Year DESC, Month DESC, TotalRevenue DESC;

-- Revenue by Category
SELECT 
    Category,
    COUNT(DISTINCT OrderID) as TotalOrders,
    SUM(Quantity) as UnitsSold,
    SUM(Revenue) as TotalRevenue,
    ROUND(SUM(Revenue) / SUM(Quantity), 2) as AvgUnitPrice,
    ROUND(COUNT(CASE WHEN OrderStatus = 'Returned' THEN 1 END) / COUNT(*) * 100, 2) as ReturnRate
FROM sales_cleaned
GROUP BY Category
ORDER BY TotalRevenue DESC;

-- Monthly Growth Rate
SELECT 
    YEAR(OrderDate) as Year,
    MONTH(OrderDate) as Month,
    SUM(Revenue) as MonthlyRevenue,
    LAG(SUM(Revenue)) OVER (ORDER BY YEAR(OrderDate), MONTH(OrderDate)) as PrevMonthRevenue,
    ROUND(
        (SUM(Revenue) - LAG(SUM(Revenue)) OVER (ORDER BY YEAR(OrderDate), MONTH(OrderDate))) / 
        LAG(SUM(Revenue)) OVER (ORDER BY YEAR(OrderDate), MONTH(OrderDate)) * 100, 2
    ) as GrowthRate
FROM sales_cleaned
GROUP BY YEAR(OrderDate), MONTH(OrderDate)
ORDER BY Year DESC, Month DESC;

-- Customer Churn Analysis
SELECT 
    Region,
    COUNT(DISTINCT CASE WHEN OrderStatus = 'Cancelled' THEN CustomerID END) as ChurnedCustomers,
    COUNT(DISTINCT CustomerID) as TotalCustomers,
    ROUND(
        COUNT(DISTINCT CASE WHEN OrderStatus = 'Cancelled' THEN CustomerID END) / 
        COUNT(DISTINCT CustomerID) * 100, 2
    ) as ChurnRate
FROM sales_cleaned
GROUP BY Region
ORDER BY ChurnRate DESC;

-- Top Products
SELECT 
    ProductName,
    Category,
    SUM(Quantity) as UnitsSold,
    SUM(Revenue) as Revenue,
    COUNT(DISTINCT OrderID) as OrderCount,
    ROUND(SUM(Revenue) / SUM(Quantity), 2) as AvgPrice
FROM sales_cleaned
GROUP BY ProductName, Category
ORDER BY Revenue DESC
LIMIT 20;

-- Payment Method Analysis
SELECT 
    PaymentMethod,
    COUNT(*) as TotalTransactions,
    SUM(Revenue) as TotalRevenue,
    ROUND(AVG(Revenue), 2) as AvgTransactionValue,
    ROUND(
        COUNT(CASE WHEN OrderStatus = 'Completed' THEN 1 END) / COUNT(*) * 100, 2
    ) as SuccessRate
FROM sales_cleaned
GROUP BY PaymentMethod
ORDER BY TotalRevenue DESC;