# Power BI Dashboard — Build Guide

This guide builds the executive **Retail Profitability** dashboard from
`data/superstore.csv` in about 30 minutes. It mirrors the SQL/Python analysis
so all three layers agree.

## 1. Get the data in

1. **Get Data → Text/CSV** → select `data/superstore.csv`.
2. In Power Query, **filter out the 806 corrupt rows**: filter the `Sales`
   column → uncheck *null* (these are the transposed header fragments).
   You should land on **9,994 rows**.
3. Set types: `Order Date` / `Ship Date` → Date, `Sales` / `Profit` → Decimal,
   `Discount` / `Quantity` → Decimal/Whole, `Postal Code` → Text (it has 11
   nulls — leave them; don't drop rows over it).
4. **Close & Apply.**

## 2. Data model

One fact table is enough for this dataset:

- `Orders` (the CSV, cleaned)
- Optional: a `Calendar` table for proper time intelligence —
  `Calendar = CALENDAR(DATE(2015,1,1), DATE(2018,12,31))`, related to
  `Orders[Order Date]`.

## 3. DAX measures

```dax
Total Sales   = SUM ( Orders[Sales] )
Total Profit  = SUM ( Orders[Profit] )
Profit Margin % = DIVIDE ( [Total Profit], [Total Sales] )
Avg Discount %  = AVERAGE ( Orders[Discount] )
Order Count   = DISTINCTCOUNT ( Orders[Order ID] )
Loss Lines    = COUNTROWS ( FILTER ( Orders, Orders[Profit] < 0 ) )
Loss Rate %   = DIVIDE ( [Loss Lines], COUNTROWS ( Orders ) )
Total Loss $  = SUMX ( FILTER ( Orders, Orders[Profit] < 0 ), Orders[Profit] )
Sales YTD     = TOTALYTD ( [Total Sales], 'Calendar'[Date] )
Profit YTD    = TOTALYTD ( [Total Profit], 'Calendar'[Date] )
```

Conditional formatting rule for margin visuals: **< 0% red, 0–10% amber,
> 10% green**.

## 4. Suggested pages

**Page 1 — Executive overview**
- KPI cards: Total Sales ($2.30M), Total Profit ($286.4K), Profit Margin %
  (12.47%), Loss Rate % (18.7%)
- Line chart: monthly Sales vs Profit (shows profit not following sales)
- Bar chart: profit margin % by Sub-Category, sorted ascending (Tables at the
  bottom in red)

**Page 2 — Discount deep-dive**
- Clustered bar: avg profit per line by discount bin (0%, 1–10%, 11–20%,
  21–30%, 31–80%) — the cliff after 20% is the story
- Table: top 10 loss-making products (Product Name, Sales, Profit) with
  conditional formatting on Profit
- Slicers: Region, Category, Segment

**Page 3 — Regional performance**
- Filled map or bar chart: margin % by Region (Central 7.92% vs West 14.94%)
- Matrix: Region × Category → Sales, Profit, Margin %
- Card: "If Central matched West's margin → +$35K profit"
  (=$501K × (14.94% − 7.92%))

## 5. Publish

Publish to the Power BI Service, grab the **"Publish to web"** embed link
(optional), and paste it into the GitHub README under a *Live dashboard*
section — or link it from the portfolio project card.
