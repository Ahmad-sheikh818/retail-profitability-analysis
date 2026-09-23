-- ============================================================================
-- Retail Profitability Analysis — SQL layer
-- Dataset: Superstore (9,994 clean order lines, 2015-01-03 → 2018-12-30)
-- Table: orders  (loaded from data/superstore.csv, corrupt rows removed)
--
-- Run:  sqlite3 superstore.db < schema.sql   (see python/analysis.py for the
--       cleaning step)  then  sqlite3 superstore.db < analysis.sql
-- ============================================================================

-- Q1. Headline KPIs -----------------------------------------------------------
SELECT
    COUNT(DISTINCT "Order ID")            AS orders,
    COUNT(*)                             AS order_lines,
    COUNT(DISTINCT "Customer ID")         AS customers,
    ROUND(SUM(Sales), 2)                 AS total_sales,
    ROUND(SUM(Profit), 2)                AS total_profit,
    ROUND(SUM(Profit) / SUM(Sales) * 100, 2) AS profit_margin_pct,
    ROUND(AVG(Discount) * 100, 2)        AS avg_discount_pct
FROM orders;

-- Q2. Profitability by category & sub-category --------------------------------
-- Which parts of the catalogue actually make money?
SELECT
    Category,
    "Sub-Category"                       AS sub_category,
    COUNT(*)                             AS lines,
    ROUND(SUM(Sales), 2)                 AS sales,
    ROUND(SUM(Profit), 2)                AS profit,
    ROUND(SUM(Profit) / SUM(Sales) * 100, 2) AS margin_pct
FROM orders
GROUP BY Category, "Sub-Category"
ORDER BY margin_pct ASC;

-- Q3. Discount vs profit -------------------------------------------------------
-- At what discount level does selling start losing money?
SELECT
    CASE
        WHEN Discount = 0               THEN '0%'
        WHEN Discount <= 0.10           THEN '1-10%'
        WHEN Discount <= 0.20           THEN '11-20%'
        WHEN Discount <= 0.30           THEN '21-30%'
        ELSE '31-80%'
    END                                  AS discount_bin,
    COUNT(*)                             AS lines,
    ROUND(AVG(Profit), 2)                AS avg_profit_per_line,
    ROUND(SUM(Profit), 2)                AS total_profit,
    ROUND(AVG(CASE WHEN Profit < 0 THEN 1.0 ELSE 0 END) * 100, 2) AS loss_rate_pct
FROM orders
GROUP BY discount_bin
ORDER BY MIN(Discount);

-- Q4. Loss-making orders -------------------------------------------------------
-- How much money is the discount strategy burning?
SELECT
    COUNT(*)                             AS loss_lines,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM orders), 2) AS pct_of_all_lines,
    ROUND(SUM(Profit), 2)                AS total_loss,
    ROUND(AVG(Discount) * 100, 2)        AS avg_discount_pct
FROM orders
WHERE Profit < 0;

-- Q5. Regional performance ------------------------------------------------------
-- Same products, different margins — where is execution weakest?
SELECT
    Region,
    COUNT(DISTINCT "Order ID")           AS orders,
    ROUND(SUM(Sales), 2)                 AS sales,
    ROUND(SUM(Profit), 2)                AS profit,
    ROUND(SUM(Profit) / SUM(Sales) * 100, 2) AS margin_pct
FROM orders
GROUP BY Region
ORDER BY margin_pct ASC;

-- Q6. Monthly trend --------------------------------------------------------------
-- Is profit keeping up with sales growth?
SELECT
    strftime('%Y-%m', "Order Date")      AS month,
    ROUND(SUM(Sales), 2)                 AS sales,
    ROUND(SUM(Profit), 2)                AS profit,
    ROUND(SUM(Profit) / SUM(Sales) * 100, 2) AS margin_pct
FROM orders
GROUP BY month
ORDER BY month;

-- Q7. Worst products ---------------------------------------------------------------
-- Name-and-shame: the SKUs destroying the most value.
SELECT
    "Product Name"                       AS product,
    "Sub-Category"                       AS sub_category,
    COUNT(*)                             AS lines,
    ROUND(SUM(Sales), 2)                 AS sales,
    ROUND(SUM(Profit), 2)                AS profit
FROM orders
GROUP BY "Product Name", "Sub-Category"
HAVING SUM(Profit) < 0
ORDER BY profit ASC
LIMIT 10;

-- Q8. Segment comparison -----------------------------------------------------------
SELECT
    Segment,
    COUNT(DISTINCT "Customer ID")         AS customers,
    ROUND(SUM(Sales), 2)                 AS sales,
    ROUND(SUM(Profit), 2)                AS profit,
    ROUND(SUM(Profit) / SUM(Sales) * 100, 2) AS margin_pct
FROM orders
GROUP BY Segment
ORDER BY margin_pct DESC;
