# Retail Profitability Analysis — Where Do Discounts Destroy Margin?


An end-to-end data analysis of 9,994 retail order lines: **SQL** for the business
questions, **Python** for exploration and visualization, and a **Power BI**
dashboard build guide. Every number below was computed from the data — no
placeholders.


🎬 Project walkthrough: [LinkedIn video walkthrough](https://www.linkedin.com/feed/update/urn:li:ugcPost:7508792600246644736/)


## Why this dataset?


I chose the Superstore retail dataset because it looks like the data a real
business analyst works with every day: orders, customers, products, regions,
**sales, discounts, and profit on every line**. It is small enough to reason
about and rich enough to answer questions a retail manager actually asks:


- Which categories make money — and which only look like they do?
- At what discount level do we start *paying* customers to buy?
- Which regions and segments execute best?
- Is profit keeping up with sales growth?


**Data source:** the "Sample – Superstore" dataset (Tableau's bundled sample,
public mirrors on GitHub/Kaggle). Period: **Jan 2015 – Dec 2018**.


> **Data quality note:** the public mirror I used shipped **806 corrupt rows**
> (7.5% of the file) — transposed header fragments like the literal strings
> `'Person'` and `'Region'` sitting in the ID columns with every measure null.
> They were identified and removed before analysis, leaving the canonical
> **9,994 order lines**. Real data is messy; cleaning it is part of the job.
> See `python/analysis.py`.


## What I did


1. **Cleaned & validated** the data in Python (pandas) — corrupt rows removed,
   date parsing checked, duplicates and nulls audited.
2. **Answered 8 business questions in SQL** (`sql/analysis.sql`) — KPIs,
   category margins, discount-vs-profit, loss analysis, regional performance,
   monthly trends, worst products, segment comparison. All queries verified
   against SQLite.
3. **Explored & visualized** in Python (`python/analysis.py`) — 4 charts in
   `images/`.
4. **Designed the executive dashboard** — build guide with data model and DAX
   measures in `powerbi/POWERBI_GUIDE.md`.


## Key findings


**Headline:** $2.30M in sales produced only $286.4K in profit — a **12.47%**
margin across 5,009 orders and 793 customers.


### 1. Discounts are the margin killer
| Discount | Avg profit / line | Lines losing money |
|---|---|---|
| 0% | +$66.90 | 0% |
| 1–10% | +$96.06 | 4.3% |
| 11–20% | +$24.74 | 14.0% |
| 21–30% | **−$45.68** | **91.6%** |
| 31–80% | **−$107.21** | **97.8%** |


- **1,871 order lines (18.7%) lost money**, burning **−$156.1K** in total.
- Loss-making lines carried an average discount of **48.1%** vs **8.1%** on
  profitable lines. The discount *is* the cause, not a coincidence.
