import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ---------- Load ----------
df = pd.read_csv("data/trades.csv")
df["entry_time"] = pd.to_datetime(df["entry_time"])
df["exit_time"] = pd.to_datetime(df["exit_time"])
df = df.sort_values("exit_time").reset_index(drop=True)
df["side"] = df["side"].str.lower()

df["hold_hours"] = (df["exit_time"] - df["entry_time"]).dt.total_seconds() / 3600
df["return_pct"] = np.where(
    df["side"] == "long",
    (df["exit_price"] - df["entry_price"]) / df["entry_price"],
    (df["entry_price"] - df["exit_price"]) / df["entry_price"],
)
df["weekday"] = df["exit_time"].dt.day_name()
df["hour"] = df["exit_time"].dt.hour
df["month"] = df["exit_time"].dt.to_period("M")
df["cum_pnl"] = df["pnl"].cumsum()

# ---------- Metrics ----------
# Use per-trade returns for Sharpe/Sortino — daily aggregation is meaningless
# with only a handful of trading days (intraday/scalping style).
trade_returns = df["pnl"]

days_span = max((df["exit_time"].max() - df["exit_time"].min()).total_seconds() / 86400, 1)
trades_per_year = len(df) / days_span * 365.25
annualization = np.sqrt(trades_per_year)

def sharpe():
    if trade_returns.std() == 0 or len(trade_returns) < 2:
        return np.nan
    return annualization * trade_returns.mean() / trade_returns.std(ddof=1)

def sortino():
    downside = trade_returns[trade_returns < 0]
    if downside.std() == 0 or len(downside) < 2:
        return np.nan
    return annualization * trade_returns.mean() / downside.std(ddof=1)

running_max = df["cum_pnl"].cummax()
drawdown = df["cum_pnl"] - running_max
max_dd = drawdown.min()

def calmar():
    if max_dd == 0:
        return np.nan
    years = days_span / 365.25
    annual_return = df["pnl"].sum() / years
    return annual_return / abs(max_dd)

gains = df.loc[df["pnl"] > 0, "pnl"].sum()
losses = df.loc[df["pnl"] < 0, "pnl"].sum()
profit_factor = gains / abs(losses) if losses != 0 else np.inf

win_rate = (df["pnl"] > 0).mean()
avg_win = df.loc[df["pnl"] > 0, "pnl"].mean() if (df["pnl"] > 0).any() else 0
avg_loss = df.loc[df["pnl"] < 0, "pnl"].mean() if (df["pnl"] < 0).any() else 0
expectancy = win_rate * avg_win + (1 - win_rate) * avg_loss

metrics = {
    "Sharpe (per-trade, annualized)": sharpe(),
    "Sortino (per-trade, annualized)": sortino(),
    "Calmar": calmar(),
    "Max Drawdown": max_dd,
    "Profit Factor": profit_factor,
    "Expectancy": expectancy,
    "Win Rate": win_rate,
    "Avg Hold Time (h)": df["hold_hours"].mean(),
    "Total PnL": df["pnl"].sum(),
    "Total Trades": len(df),
    "Trading Days Span": round(days_span, 1),
    "Trades/Year (annualized)": round(trades_per_year, 0),
}

with open("metrics.txt", "w") as f:
    for k, v in metrics.items():
        line = f"{k}: {v:,.4f}" if isinstance(v, float) else f"{k}: {v}"
        print(line)
        f.write(line + "\n")

# ---------- Plots ----------
plt.figure(figsize=(10, 5))
plt.plot(df["exit_time"], df["cum_pnl"], color="green")
plt.title("Equity Curve"); plt.xlabel("Time"); plt.ylabel("Cumulative PnL")
plt.tight_layout(); plt.savefig("equity_curve.png"); plt.close()

plt.figure(figsize=(10, 5))
plt.fill_between(df["exit_time"], drawdown, 0, color="red")
plt.title("Drawdown"); plt.xlabel("Time"); plt.ylabel("Drawdown")
plt.tight_layout(); plt.savefig("drawdown.png"); plt.close()

plt.figure(figsize=(8, 5))
plt.hist(df["return_pct"], bins=60, color="steelblue")
plt.title("Distribution of Returns"); plt.xlabel("Return %")
plt.tight_layout(); plt.savefig("returns_hist.png"); plt.close()

monthly = df.groupby("month")["pnl"].sum()
plt.figure(figsize=(10, 5))
colors = ["green" if v >= 0 else "red" for v in monthly.values]
plt.bar(monthly.index.astype(str), monthly.values, color=colors)
plt.title("Monthly Returns"); plt.xticks(rotation=45)
plt.tight_layout(); plt.savefig("monthly_returns.png"); plt.close()

roll = trade_returns.rolling(50)  # rolling window over trades, not days
rolling_sharpe = annualization * roll.mean() / roll.std(ddof=1)
plt.figure(figsize=(10, 5))
plt.plot(range(len(rolling_sharpe)), rolling_sharpe.values, color="purple")
plt.title("Rolling Sharpe (50 trades)"); plt.xlabel("Trade #")
plt.tight_layout(); plt.savefig("rolling_sharpe.png"); plt.close()

pivot = df.pivot_table(index="weekday", columns="hour", values="pnl", aggfunc="sum", fill_value=0)
order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
pivot = pivot.reindex([d for d in order if d in pivot.index])
plt.figure(figsize=(12, 5))
plt.imshow(pivot, cmap="RdYlGn", aspect="auto")
plt.colorbar(label="PnL")
plt.yticks(range(len(pivot.index)), pivot.index)
plt.xticks(range(len(pivot.columns)), pivot.columns)
plt.title("PnL Heatmap: Weekday x Hour")
plt.tight_layout(); plt.savefig("heatmap.png"); plt.close()

lvs = df.groupby("side")["pnl"].sum()
plt.figure(figsize=(6, 5))
plt.bar(lvs.index, lvs.values, color=["green", "red"])
plt.title("Long vs Short PnL")
plt.tight_layout(); plt.savefig("long_vs_short.png"); plt.close()

print("\nDone. Check the .png files and metrics.txt in this folder.")