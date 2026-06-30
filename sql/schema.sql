-- Create Database
CREATE DATABASE IF NOT EXISTS sales_db;
USE sales_db;

-- Main Sales Table
CREATE TABLE IF NOT EXISTS sales (
    OrderID VARCHAR(10) PRIMARY KEY,
    OrderDate DATETIME NOT NULL,
    CustomerID VARCHAR(10) NOT NULL,
    CustomerName VARCHAR(100) NOT NULL,
    Email VARCHAR(100),
    Phone VARCHAR(20),
    Region VARCHAR(50) NOT NULL,
    Category VARCHAR(50) NOT NULL,
    ProductName VARCHAR(100) NOT NULL,
    Quantity INT NOT NULL,
    UnitPrice DECIMAL(10, 2) NOT NULL,
    Discount DECIMAL(5, 2),
    PaymentMethod VARCHAR(50),
    OrderStatus VARCHAR(20),
    TotalAmount DECIMAL(12, 2) NOT NULL,
    DiscountAmount DECIMAL(12, 2),
    Revenue DECIMAL(12, 2) NOT NULL,
    INDEX idx_region (Region),
    INDEX idx_category (Category),
    INDEX idx_date (OrderDate),
    INDEX idx_status (OrderStatus)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Customer Dimension Table
CREATE TABLE IF NOT EXISTS customers (
    CustomerID VARCHAR(10) PRIMARY KEY,
    CustomerName VARCHAR(100),
    Email VARCHAR(100),
    Phone VARCHAR(20),
    RegionPreference VARCHAR(50),
    FirstPurchaseDate DATETIME,
    TotalSpend DECIMAL(15, 2),
    INDEX idx_email (Email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Regional Performance Table
CREATE TABLE IF NOT EXISTS regional_performance (
    RegionPerformanceID INT AUTO_INCREMENT PRIMARY KEY,
    Region VARCHAR(50) NOT NULL,
    Year INT NOT NULL,
    Month INT NOT NULL,
    TotalRevenue DECIMAL(15, 2),
    TotalOrders INT,
    AverageOrderValue DECIMAL(10, 2),
    ChurnRate DECIMAL(5, 2),
    UNIQUE KEY unique_region_month (Region, Year, Month),
    INDEX idx_region_date (Region, Year, Month)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Category Performance Table
CREATE TABLE IF NOT EXISTS category_performance (
    CategoryPerformanceID INT AUTO_INCREMENT PRIMARY KEY,
    Category VARCHAR(50) NOT NULL,
    Year INT NOT NULL,
    Month INT NOT NULL,
    TotalRevenue DECIMAL(15, 2),
    UnitsSold INT,
    ReturnRate DECIMAL(5, 2),
    INDEX idx_category_date (Category, Year, Month)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;