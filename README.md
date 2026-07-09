# Trade Analytics Dashboard

A lightweight, dependency-minimal tool for analyzing trading performance from a CSV log of trades. It computes standard quant performance metrics and generates a set of visualizations — no server, no browser, no dashboard framework required.

## What it does

Given a CSV of individual trades, the script computes:

- **Sharpe Ratio** (annualized, per-trade basis)
- **Sortino Ratio** (annualized, per-trade basis)
- **Calmar Ratio**
- **Max Drawdown**
- **Profit Factor**
- **Expectancy**
- **Win Rate**
- **Average Hold Time**
- **PnL by weekday / hour** (heatmap)
- **Long vs Short** performance breakdown
- **Distribution of returns**

And generates the following charts, saved as PNG files:

| File | Description |
|---|---|
| `equity_curve.png` | Cumulative PnL over time |
| `drawdown.png` | Drawdown from running peak equity |
| `returns_hist.png` | Histogram of per-trade returns |
| `monthly_returns.png` | PnL aggregated by month |
| `rolling_sharpe.png` | Rolling Sharpe ratio over a trailing trade window |
| `heatmap.png` | PnL heatmap by weekday × hour |
| `long_vs_short.png` | Total PnL comparison, long vs short positions |

All metrics are also printed to the console and saved to `metrics.txt`.

## Project structure

```
trade_analytics_dashboard/
├── data/
│   └── trades.csv       # your trade log (input)
├── analyze.py           # single script: computes metrics + generates charts
└── requirements.txt
```

## Input format (`trades.csv`)

Required columns:

| Column | Type | Description |
|---|---|---|
| `entry_time` | datetime | Trade entry timestamp |
| `exit_time` | datetime | Trade exit timestamp |
| `symbol` | string | Ticker / instrument |
| `side` | string | `long` or `short` |
| `entry_price` | float | Entry price |
| `exit_price` | float | Exit price |
| `size` | float | Position size |
| `pnl` | float | Realized profit/loss for the trade |

Example row:
```
entry_time,exit_time,symbol,side,entry_price,exit_price,size,pnl
2024-01-02 09:31:00,2024-01-02 10:15:00,AAPL,long,185.20,186.50,100,130.0
```

## Setup

```bash
pip3 install -r requirements.txt
```

## Usage

Place your trade log at `data/trades.csv`, then run:

```bash
python3 analyze.py
```

Output (`metrics.txt` and all `.png` charts) is saved in the project root.

## Notes on methodology

- **Sharpe / Sortino** are computed on a **per-trade** basis and annualized using the actual observed trading frequency (`trades_per_year`, derived from the timespan of the data), rather than assuming daily bars. This makes the metrics meaningful for both low-frequency and high-frequency (intraday/scalping) strategies.
- **Calmar Ratio** annualizes total PnL over the actual date range of the data, then divides by max drawdown.
- Metrics computed on **short time spans or small trade samples are statistically noisy** — annualized ratios extrapolated from a few days of data should be treated as rough indicators, not precise risk estimates. Longer histories (months+) produce more reliable results.
- `return_pct` is calculated per trade (relative to entry price), directionally adjusted for long/short.

## Requirements

- Python 3.9+
- pandas
- numpy
- matplotlib

## Sample data disclaimer

This project was built and tested using synthetic/randomly generated trade data for demonstration purposes. Replace `data/trades.csv` with real trade history to get meaningful results.