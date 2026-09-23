"""
Retail Profitability Analysis — Superstore dataset
Runs the full analysis: validation, KPIs, category/region/discount
deep-dives, monthly trends, and saves charts to ../images/.

Run:  python analysis.py
Requires: pandas, matplotlib, numpy
"""
import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data", "superstore.csv")
IMG = os.path.join(BASE, "images")
os.makedirs(IMG, exist_ok=True)

# ---------- brand style (matches portfolio) ----------
BG, FG, MUTED, LIME, BLUE, CORAL = "#10120f", "#f0f1e9", "#a6aaa1", "#dafa4c", "#bbd4fb", "#f6b9aa"
plt.rcParams.update({
    "figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG,
    "text.color": FG, "axes.labelcolor": FG, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.edgecolor": "#353a31", "grid.color": "#2a2e27", "grid.alpha": 0.6,
    "font.family": "DejaVu Sans",
})

# ---------- load & validate ----------
for enc in ("utf-8-sig", "utf-8", "latin-1"):
    try:
        df = pd.read_csv(DATA, encoding=enc)
        break
    except UnicodeDecodeError:
        continue

print("=" * 60)
print("DATA VALIDATION")
print("=" * 60)
print(f"Raw rows: {len(df):,}")

# Data quality: this mirror ships 806 corrupt rows (transposed header
# fragments — e.g. the literal strings 'Person'/'Region' in the ID columns,
# every measure null). Real-world data is messy; drop them and verify.
junk = df[df["Sales"].isna()]
print(f"Corrupt rows found (null Sales, header fragments): {len(junk):,}")
print(f"Example junk Row ID values: {junk['Row ID'].dropna().unique()[:5].tolist()}")
df = df.dropna(subset=["Sales"]).copy()
df["Order Date"] = pd.to_datetime(df["Order Date"], format="mixed", dayfirst=False)
df["Ship Date"] = pd.to_datetime(df["Ship Date"], format="mixed", dayfirst=False)

print(f"Clean rows: {len(df):,}")
print(f"Period: {df['Order Date'].min().date()} → {df['Order Date'].max().date()}")
print(f"Duplicate Row IDs: {df['Row ID'].duplicated().sum()}")
print(f"Missing values (excl. known Postal Code gaps):\n"
      f"{df.isna().sum()[df.isna().sum() > 0]}")
print(f"Negative sales rows: {(df['Sales'] < 0).sum()}")

# ---------- headline KPIs ----------
sales, profit = df["Sales"].sum(), df["Profit"].sum()
orders, customers = df["Order ID"].nunique(), df["Customer ID"].nunique()
print("\n" + "=" * 60)
print("HEADLINE KPIs")
print("=" * 60)
print(f"Total sales:   ${sales:,.2f}")
print(f"Total profit:  ${profit:,.2f}")
print(f"Profit margin: {profit / sales * 100:.2f}%")
print(f"Orders: {orders:,} | Order lines: {len(df):,} | Customers: {customers:,}")
print(f"Avg discount: {df['Discount'].mean() * 100:.2f}%")

# ---------- 1. category / sub-category profitability ----------
cat = df.groupby("Category").agg(sales=("Sales", "sum"), profit=("Profit", "sum"),
                                 orders=("Order ID", "nunique"))
cat["margin_pct"] = cat["profit"] / cat["sales"] * 100
sub = df.groupby("Sub-Category").agg(sales=("Sales", "sum"), profit=("Profit", "sum"),
                                     orders=("Order ID", "nunique"))
sub["margin_pct"] = sub["profit"] / sub["sales"] * 100
sub = sub.sort_values("margin_pct")
print("\nCATEGORY MARGIN:\n", cat.round(2).to_string())
print("\nWORST SUB-CATEGORIES BY MARGIN:\n", sub.head(5).round(2).to_string())
print("\nBEST SUB-CATEGORIES BY MARGIN:\n", sub.tail(3).round(2).to_string())

fig, ax = plt.subplots(figsize=(9, 7))
colors = [CORAL if v < 0 else (LIME if v > 25 else BLUE) for v in sub["margin_pct"]]
ax.barh(sub.index, sub["margin_pct"], color=colors, edgecolor="none", height=0.62)
ax.axvline(0, color=FG, linewidth=0.8)
ax.set_xlabel("Profit margin %")
ax.set_title("Profit margin by sub-category", fontsize=13, pad=12, color=FG)
ax.grid(axis="x", linestyle="--")
for i, v in enumerate(sub["margin_pct"]):
    ax.text(v + (0.6 if v >= 0 else -0.6), i, f"{v:.1f}%", va="center",
            ha="left" if v >= 0 else "right", fontsize=8, color=FG)
fig.tight_layout(); fig.savefig(f"{IMG}/profit_margin_by_subcategory.png", dpi=150); plt.close(fig)

# ---------- 2. discount vs profit ----------
df["Discount bin"] = pd.cut(df["Discount"], bins=[-0.01, 0, 0.1, 0.2, 0.3, 0.81],
                            labels=["0%", "1–10%", "11–20%", "21–30%", "31–80%"])
disc = df.groupby("Discount bin", observed=True).agg(
    avg_profit=("Profit", "mean"), total_profit=("Profit", "sum"),
    lines=("Profit", "size"), loss_rate=("Profit", lambda s: (s < 0).mean() * 100))
print("\nDISCOUNT BIN ANALYSIS:\n", disc.round(2).to_string())
loss_orders = df[df["Profit"] < 0]
print(f"\nLoss-making order lines: {len(loss_orders):,} ({len(loss_orders)/len(df)*100:.1f}%)")
print(f"Total loss from them: ${loss_orders['Profit'].sum():,.2f}")
print(f"Avg discount on LOSS lines: {loss_orders['Discount'].mean()*100:.1f}%")
print(f"Avg discount on PROFIT lines: {df[df['Profit'] >= 0]['Discount'].mean()*100:.1f}%")

fig, ax = plt.subplots(figsize=(9, 5.2))
x = np.arange(len(disc))
bars = ax.bar(x, disc["avg_profit"], color=[CORAL if v < 0 else LIME for v in disc["avg_profit"]],
              edgecolor="none", width=0.62)
ax.set_xticks(x); ax.set_xticklabels(disc.index)
ax.set_ylabel("Average profit per order line ($)")
ax.set_title("Bigger discounts → thinner (then negative) profit", fontsize=13, pad=12, color=FG)
ax.axhline(0, color=FG, linewidth=0.8); ax.grid(axis="y", linestyle="--")
for b, v, n in zip(bars, disc["avg_profit"], disc["lines"]):
    ax.text(b.get_x() + b.get_width()/2, b.get_height() + (2 if v >= 0 else -6),
            f"${v:,.0f}\n({n:,} lines)", ha="center", va="bottom" if v >= 0 else "top",
            fontsize=8, color=FG)
fig.tight_layout(); fig.savefig(f"{IMG}/discount_vs_profit.png", dpi=150); plt.close(fig)

# ---------- 3. region & segment ----------
reg = df.groupby("Region").agg(sales=("Sales", "sum"), profit=("Profit", "sum"),
                               orders=("Order ID", "nunique"))
reg["margin_pct"] = reg["profit"] / reg["sales"] * 100
reg = reg.sort_values("margin_pct")
seg = df.groupby("Segment").agg(sales=("Sales", "sum"), profit=("Profit", "sum"))
seg["margin_pct"] = seg["profit"] / seg["sales"] * 100
print("\nREGION:\n", reg.round(2).to_string())
print("\nSEGMENT:\n", seg.round(2).to_string())

fig, ax1 = plt.subplots(figsize=(9, 5.2))
x = np.arange(len(reg))
ax1.bar(x, reg["sales"], color=BLUE, edgecolor="none", width=0.55, label="Sales")
ax1.set_xticks(x); ax1.set_xticklabels(reg.index)
ax1.set_ylabel("Sales ($)", color=BLUE)
ax2 = ax1.twinx()
ax2.plot(x, reg["margin_pct"], color=LIME, marker="o", linewidth=2.5, markersize=8, label="Margin %")
ax2.set_ylabel("Profit margin %", color=LIME)
ax2.tick_params(axis="y", colors=LIME)
ax1.set_title("Sales are spread out — margins are not", fontsize=13, pad=12, color=FG)
for i, v in enumerate(reg["margin_pct"]):
    ax2.text(i, v + 0.35, f"{v:.1f}%", ha="center", fontsize=9, color=LIME, weight="bold")
fig.tight_layout(); fig.savefig(f"{IMG}/region_performance.png", dpi=150); plt.close(fig)

# ---------- 4. monthly trend ----------
df["Month"] = df["Order Date"].dt.to_period("M").dt.to_timestamp()
mon = df.groupby("Month").agg(sales=("Sales", "sum"), profit=("Profit", "sum")).sort_index()
mon["margin_pct"] = mon["profit"] / mon["sales"] * 100
print(f"\nBest month (sales): {mon['sales'].idxmax().date()} (${mon['sales'].max():,.0f})")
print(f"Worst month (profit): {mon['profit'].idxmin().date()} (${mon['profit'].min():,.0f})")
print(f"Months with negative profit: {(mon['profit'] < 0).sum()} of {len(mon)}")

fig, ax1 = plt.subplots(figsize=(11, 5.2))
ax1.fill_between(mon.index, mon["sales"], color=BLUE, alpha=0.25)
ax1.plot(mon.index, mon["sales"], color=BLUE, linewidth=2, label="Sales")
ax1.set_ylabel("Monthly sales ($)", color=BLUE)
ax2 = ax1.twinx()
ax2.plot(mon.index, mon["profit"], color=LIME, linewidth=2, label="Profit")
ax2.axhline(0, color=CORAL, linewidth=1, linestyle="--")
ax2.set_ylabel("Monthly profit ($)", color=LIME)
ax2.tick_params(axis="y", colors=LIME)
ax1.set_title("Sales grow steadily — profit does not follow", fontsize=13, pad=12, color=FG)
fig.tight_layout(); fig.savefig(f"{IMG}/monthly_trend.png", dpi=150); plt.close(fig)

# ---------- 5. worst products ----------
prod = df.groupby("Product Name").agg(profit=("Profit", "sum"), sales=("Sales", "sum"),
                                      lines=("Sales", "size"))
worst = prod.sort_values("profit").head(8)
print("\nMOST LOSS-MAKING PRODUCTS:\n", worst.round(2).to_string())

print("\nCharts saved to ../images/. Done.")
