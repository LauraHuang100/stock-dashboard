# SKILL.md — Stock Dashboard Engineering Guide

## Project Purpose

This project generates a stock market dashboard using Python.
The dashboard is automatically updated daily via GitHub Actions and published through GitHub Pages.

Primary goals:
- Accurate market data
- Reliable automated updates
- Clear portfolio visualization
- Fast debugging
- Maintainable code structure
- Mobile-friendly HTML output

---

# Core Principles

1. Accuracy over aesthetics
2. Never silently change financial calculations
3. Preserve automation compatibility
4. Minimize breaking changes
5. Validate all ticker data
6. Prefer deterministic calculations
7. Keep dashboard generation idempotent

---

# Technology Stack

- Python 3.x
- VS Code
- GitHub Actions
- GitHub Pages
- pandas
- yfinance
- matplotlib / plotly
- HTML/CSS templates
- Gmail SMTP notifications

---

# Expected Repository Structure

/project-root
    dashboard.py
    data/
    charts/
    output/
    templates/
    utils/
    tests/
    .github/workflows/
    requirements.txt
    README.md
    SKILL.md

---

# Rules for AI Code Modifications

## When modifying code:

- Never remove existing calculations unless explicitly instructed
- Preserve function signatures when possible
- Avoid introducing unnecessary dependencies
- Keep compatibility with GitHub Actions Linux runners
- Avoid hardcoded local paths
- Use environment variables for secrets
- Add logging for critical operations
- Add comments for non-obvious financial logic

---

# Financial Data Accuracy Rules

## Price Handling

- Use adjusted close when analyzing returns
- Use close price for daily dashboard display unless otherwise specified
- Validate that market dates are trading days
- Handle weekends and holidays gracefully

## ETF / Portfolio Calculations

- Weight calculations must sum to 100%
- Display percentages consistently
- Use float precision carefully
- Never mix adjusted and unadjusted prices in the same calculation

## Validation Checks

Before publishing dashboard:
- Verify all tickers downloaded successfully
- Detect empty DataFrames
- Detect stale market data
- Validate date ranges
- Confirm charts generated successfully

---

# Dashboard Design Standards

## Visual Standards

- Mobile-friendly layout
- Responsive charts
- Dark mode compatibility preferred
- Minimize clutter
- Consistent color scheme

## Information Hierarchy

Priority order:
1. Portfolio value
2. Daily change
3. Holdings allocation
4. Sector exposure
5. Performance charts
6. Market indicators

---

# Preferred Python Patterns

## Use:

- pandas vectorized operations
- reusable utility functions
- typed helper functions where useful
- pathlib instead of raw string paths
- f-strings
- centralized config

## Avoid:

- duplicated logic
- global mutable state
- deeply nested code
- magic constants
- unnecessary loops over DataFrames

---

# Error Handling Standards

Critical operations must:
- use try/except
- log meaningful errors
- fail gracefully
- continue processing non-critical sections

Examples:
- missing ticker
- API timeout
- partial market data
- failed chart rendering

---

# GitHub Actions Rules

## Workflow Requirements

- Must run unattended
- Must support cron execution
- Must fail loudly on bad data
- Must not expose secrets
- Should generate debug logs

## Deployment

Generated dashboard output should:
- overwrite previous output cleanly
- publish to GitHub Pages automatically
- avoid unnecessary commits

---

# Testing Expectations

When modifying logic:
- verify dashboard generation completes
- validate portfolio math
- check charts render
- confirm HTML output exists
- test on fresh environment when possible

---

# Performance Expectations

Optimize for:
- reliability first
- readability second
- speed third

Avoid:
- unnecessary API calls
- repeated downloads
- loading entire histories if not needed

---

# Preferred Improvements

High-value future enhancements:
- caching layer
- retry logic
- modular chart system
- configuration file
- unit tests
- portfolio analytics
- benchmark comparison
- drawdown analysis
- factor exposure analysis
- alerting system
- SQLite storage
- market regime indicators

---

# AI Assistant Instructions

When helping with this project:

1. Explain WHY changes are made
2. Show minimal diff when possible
3. Preserve backward compatibility
4. Point out financial-data edge cases
5. Warn before architectural rewrites
6. Suggest validation steps
7. Assume automation reliability matters

If uncertain:
- prefer conservative modifications
- ask before changing financial logic
- avoid speculative refactors

---

# Known Edge Cases

- Weekends and holidays
- Yahoo Finance missing data
- Ticker delistings
- ETF holdings changes
- Market close timing
- Timezone inconsistencies
- GitHub Actions environment differences

---

# Definition of Done

A change is complete only if:
- dashboard builds successfully
- charts render
- financial calculations validate
- GitHub Action still works
- HTML output publishes correctly
- no secrets exposed