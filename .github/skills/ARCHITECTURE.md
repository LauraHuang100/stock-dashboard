# ARCHITECTURE.md

# System Overview

This project is a public market dashboard generator.

The dashboard:
1. Downloads market and ETF data
2. Calculates technical indicators
3. Generates charts and analytics
4. Builds responsive HTML output
5. Publishes automatically via GitHub Pages

The system is designed for:
- unattended daily execution
- financial data accuracy
- public consumption
- mobile-friendly rendering
- modular extensibility
- GitHub Actions reliability

This dashboard DOES NOT:
- track personal portfolios
- expose private holdings
- display account allocations
- store brokerage credentials

---

# High-Level Architecture

```text
                ┌────────────────────┐
                │ GitHub Actions Cron│
                └─────────┬──────────┘
                          │
                          ▼
                ┌────────────────────┐
                │ Python Entry Script│
                │   dashboard.py     │
                └─────────┬──────────┘
                          │
         ┌────────────────┼────────────────┐
         ▼                ▼                ▼
 ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
 │ Market Data  │ │ Technical    │ │ Config/Data  │
 │ Download     │ │ Indicators   │ │ Loading      │
 └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
        │                │                │
        └────────────────┼────────────────┘
                         ▼
               ┌──────────────────┐
               │ Market Analytics │
               └────────┬─────────┘
                        ▼
               ┌──────────────────┐
               │ Chart Generation │
               └────────┬─────────┘
                        ▼
               ┌──────────────────┐
               │ HTML Rendering   │
               └────────┬─────────┘
                        ▼
               ┌──────────────────┐
               │ GitHub Pages     │
               │ Published Output │
               └──────────────────┘
```

---

# Core Components

## 1. Data Acquisition Layer

Responsible for:
- downloading ticker data
- retrieving ETF information
- retrieving macro indicators
- validating trading dates
- handling API failures

Typical libraries:
- yfinance
- pandas
- requests

Key concerns:
- stale data
- missing tickers
- market holidays
- API throttling
- timezone consistency

---

## 2. Technical Indicator Layer

Responsible for:
- RSI calculation
- moving averages
- golden/death crosses
- momentum indicators
- volatility calculations

Indicators should:
- use consistent lookback periods
- validate sufficient historical data
- avoid recalculating redundant series
- support modular reuse

---

## 3. Market Analytics Layer

Responsible for:
- ETF monitoring
- sector tracking
- market trend analysis
- benchmark comparison
- macro visualization
- relative strength metrics

This layer should:
- avoid portfolio-specific assumptions
- remain public-data only
- support reusable analytics modules

---

## 4. Visualization Layer

Responsible for:
- chart generation
- responsive layouts
- mobile readability
- consistent styling

Preferred outputs:
- PNG charts
- Plotly HTML charts
- responsive HTML sections

Charts should:
- degrade gracefully
- avoid clutter
- support mobile devices

---

## 5. HTML Rendering Layer

Responsible for:
- dashboard assembly
- template rendering
- chart embedding
- responsive formatting

Preferred approach:
- template-driven rendering
- minimal inline logic
- reusable sections/components

---

## 6. Automation Layer

Implemented using:
- GitHub Actions
- cron schedules

Responsibilities:
- scheduled execution
- dependency installation
- dashboard publishing
- log visibility
- deployment validation

---

# Recommended Directory Structure

```text
project-root/
│
├── dashboard.py
├── requirements.txt
├── README.md
│
├── skills/
│   ├── SKILL.md
│   ├── ARCHITECTURE.md
│   ├── DATA_FLOW.md
│   ├── TESTING.md
│   ├── DEPLOYMENT.md
│   ├── AI_CONTEXT.md
│   └── INDICATORS.md
│
├── config/
├── data/
├── output/
├── charts/
├── templates/
├── logs/
├── utils/
├── tests/
│
└── .github/
    └── workflows/
```

---

# Design Principles

## Reliability First

The dashboard must:
- run unattended
- fail gracefully
- recover from partial API failures

---

## Financial Accuracy

The system prioritizes:
- validated calculations
- deterministic outputs
- consistent indicator definitions

---

## Public Safety

The dashboard must never:
- expose secrets
- expose private allocations
- expose account information

---

## Modularity

Each subsystem should:
- have clear inputs/outputs
- support isolated testing
- minimize cross-dependencies

---

# Future Architecture Goals

Potential future enhancements:
- caching layer
- SQLite storage
- plugin-based indicators
- macro data integrations
- alerting system
- factor analysis engine
- historical snapshot archive