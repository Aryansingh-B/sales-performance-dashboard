# Power BI Dashboard Setup Guide

## 📊 Dashboard Overview
12+ KPIs enabling real-time business performance monitoring

## Getting Started

### Step 1: Connect Data Source
1. Open Power BI Desktop
2. Get Data → CSV
3. Select: `data/processed/sales_data_cleaned.csv`
4. Load Data

### Step 2: Data Modeling
Create these tables in Power BI:
- **sales**: Main fact table
- **date_dim**: Date hierarchy (Date, Month, Quarter, Year)
- **region_dim**: Region lookup
- **category_dim**: Category lookup

### Step 3: Key Measures (DAX)
```dax
# Total Revenue
TotalRevenue = SUM(sales[Revenue])

# Total Orders
TotalOrders = COUNTA(sales[OrderID])

# Average Order Value
AOV = DIVIDE([TotalRevenue], [TotalOrders])

# Churn Rate
ChurnRate = DIVIDE(
    CALCULATE([TotalOrders], sales[OrderStatus] = "Cancelled"),
    [TotalOrders]
)

# Growth Rate (MoM)
GrowthRate = DIVIDE(
    [TotalRevenue] - CALCULATE([TotalRevenue], PREVIOUSMONTH(date_dim[Date])),
    CALCULATE([TotalRevenue], PREVIOUSMONTH(date_dim[Date]))
)

# Return Rate
ReturnRate = DIVIDE(
    CALCULATE([TotalOrders], sales[OrderStatus] = "Returned"),
    [TotalOrders]
)
```

### Step 4: Create Dashboard Pages

#### Page 1: Executive Overview
- KPI Cards: Revenue, Orders, AOV, Customers
- Revenue Trend (Line Chart)
- Revenue by Region (Map/Bar)
- Revenue by Category (Pie/Bar)

#### Page 2: Regional Analysis
- Revenue by Region (Map)
- Growth Rate by Region (Table)
- Churn Rate by Region (Clustered Bar)
- Top Customers by Region (Table)

#### Page 3: Product Performance
- Revenue by Category (Column Chart)
- Top 20 Products (Horizontal Bar)
- Return Rate by Category (Gauge)
- Units Sold Trend (Area Chart)

#### Page 4: Customer Insights
- Customer Count (Card)
- Revenue per Customer (Gauge)
- Customer Segmentation (Scatter)
- Payment Method Distribution (Donut)

#### Page 5: Operations
- Order Status Distribution (Pie)
- Payment Method Performance (Table)
- Processing Time Analysis
- Discount Impact Analysis

### Step 5: Publishing
1. File → Publish → Select workspace
2. Share dashboard with stakeholders
3. Set up automatic refresh: Daily (Power BI Pro)

## 💾 File Export
- Reports→ Export to PDF
- Visuals → Export data

## 🔄 Auto-Refresh Setup
Power BI Service → Dataset Settings → Scheduled Refresh
- Frequency: Daily
- Time: 02:00 AM (off-peak)
- Enable notifications

## 📱 Mobile Optimization
- Use responsive design layout
- Pin key visuals to mobile dashboard
- Create simplified mobile-specific page