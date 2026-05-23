# DATA_FLOW.md

# Overview

This document describes how data moves through the dashboard system.

The dashboard follows this pipeline:

```text
Market Data Sources
        ↓
Data Validation
        ↓
Transformation
        ↓
Technical Indicators
        ↓
Market Analytics
        ↓
Visualization
        ↓
HTML Rendering
        ↓
GitHub Pages Deployment
```

---

# Step 1 — External Data Sources

Primary sources:
- Yahoo Finance
- ETF data
- market indices
- treasury yields
- volatility indices

Potential future sources:
- FRED
- Alpha Vantage
- Polygon
- Financial Modeling Prep

---

# Step 2 — Raw Data Download

## Inputs

Ticker lists:
```python
["VOO", "QQQM", "SMH", "DRAM"]
```

## Outputs

Raw pandas DataFrames:
- OHLCV data
- adjusted close
- volume
- dividends
- metadata

---

# Step 3 — Validation Layer

Validation checks:
- empty DataFrames
- stale timestamps
- missing columns
- NaN values
- trading-day alignment

If validation fails:
- log detailed error
- skip non-critical asset
- halt on critical failures

---

# Step 4 — Transformation Layer

Transforms raw data into:
- normalized formats
- rolling windows
- daily returns
- chart-ready datasets
- analytics-ready metrics

Examples:
- adjusted close extraction
- rolling averages
- percentage changes
- normalized performance

---

# Step 5 — Technical Indicator Processing

Indicators generated:
- RSI
- moving averages
- rolling volatility
- momentum indicators
- relative strength

Indicator requirements:
- use adjusted close prices
- validate sufficient history
- handle weekends/holidays gracefully
- prevent NaN leakage into dashboard

---

# Step 6 — Market Analytics Layer

Analytics generated:
- ETF monitoring
- sector tracking
- benchmark comparison
- market trend analysis
- technical summaries

Outputs:
- summary tables
- chart-ready metrics
- HTML-renderable sections

---

# Step 7 — Visualization Layer

Charts generated:
- line charts
- RSI charts
- bar charts
- heatmaps
- trend indicators

Outputs:
- PNG
- SVG
- Plotly HTML

Charts stored in:
```text
/charts/
```

---

# Step 8 — HTML Rendering

Inputs:
- metrics
- indicators
- chart paths
- templates

Outputs:
```text
/output/index.html
```

Responsibilities:
- responsive layout
- section ordering
- chart embedding
- mobile formatting

---

# Step 9 — Deployment

GitHub Actions:
1. runs dashboard build
2. generates charts/HTML
3. publishes dashboard
4. updates GitHub Pages

Final output:
```text
https://<github-user>.github.io/<repo-name>/
```

---

# Error Flow

## Recoverable Errors

Examples:
- single ticker download failure
- optional chart failure
- temporary API timeout

Action:
- log warning
- continue execution

---

## Critical Errors

Examples:
- dashboard HTML generation failure
- missing required data
- output directory failure

Action:
- stop execution
- fail GitHub Action
- surface logs clearly

---

# Logging Flow

Logs should include:
- timestamps
- execution duration
- failed tickers
- generated charts
- indicator calculation failures

Log destinations:
- console
- GitHub Actions logs
- optional file logs

---

# Future Data Flow Enhancements

Potential additions:
- caching layer
- database persistence
- incremental updates
- historical snapshots
- multi-source reconciliation