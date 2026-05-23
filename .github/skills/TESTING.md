# TESTING.md

# Testing Philosophy

The dashboard prioritizes:
1. financial accuracy
2. automation reliability
3. rendering stability
4. technical indicator correctness

Testing focuses on preventing:
- incorrect calculations
- broken charts
- deployment failures
- stale data publication
- invalid indicators

---

# Testing Levels

## 1. Unit Tests

Test isolated functions.

Examples:
- RSI calculations
- moving averages
- rolling windows
- date handling

Framework:
```bash
pytest
```

Example:
```python
def test_rsi_bounds():
    assert df["RSI"].between(0, 100).all()
```

---

## 2. Integration Tests

Test subsystem interactions.

Examples:
- download + indicator generation
- indicators + charts
- rendering + deployment

Goals:
- validate pipeline continuity
- detect schema mismatches

---

## 3. End-to-End Tests

Run full dashboard generation.

Expected result:
- dashboard builds successfully
- charts render
- HTML generated
- no exceptions thrown

---

# Technical Indicator Validation

Validate:
- RSI values remain between 0 and 100
- sufficient lookback history exists
- rolling windows align correctly
- no invalid NaN propagation

---

# Data Validation Tests

Validate:
- ticker availability
- trading-day alignment
- duplicate rows
- timezone consistency

---

# Rendering Tests

Validate:
- HTML generated successfully
- chart files exist
- responsive layout intact
- no broken image references

---

# GitHub Actions Tests

Ensure:
- cron workflow executes
- dependencies install correctly
- deployment succeeds
- GitHub Pages updates correctly

---

# Public Dashboard Validation

Ensure dashboard:
- contains no secrets
- contains no private allocations
- contains no account-specific information

---

# Manual Testing Checklist

Before major releases:

## Data
- verify ticker prices
- verify RSI calculations
- verify date ranges

## Charts
- verify labels
- verify scales
- verify mobile rendering

## Deployment
- verify GitHub Pages updated
- verify latest commit deployed
- verify dashboard publicly accessible

---

# Common Failure Modes

## Yahoo Finance Issues

Symptoms:
- missing data
- delayed prices
- partial downloads

Mitigation:
- retries
- validation checks
- fallback handling

---

## Indicator Failures

Symptoms:
- RSI outside 0-100
- excessive NaN values
- chart gaps

Mitigation:
- lookback validation
- rolling window checks
- NaN filtering

---

## Chart Rendering Failures

Symptoms:
- missing charts
- empty files
- rendering exceptions

Mitigation:
- file existence checks
- exception handling

---

# Suggested Test Structure

```text
/tests/
│
├── test_data.py
├── test_indicators.py
├── test_charts.py
├── test_rendering.py
└── test_pipeline.py
```

---

# Future Testing Improvements

Potential additions:
- snapshot testing
- HTML regression testing
- CI coverage reporting
- mock market data
- visual diff testing