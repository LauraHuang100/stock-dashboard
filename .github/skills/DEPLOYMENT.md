# DEPLOYMENT.md

# Deployment Overview

The dashboard is automatically deployed using:
- GitHub Actions
- GitHub Pages

Deployment is designed to:
- run unattended
- publish daily updates
- support public viewing
- minimize manual maintenance

---

# Public Dashboard Requirements

The dashboard is public-facing.

Requirements:
- no private portfolio data
- no account-specific analytics
- no secrets exposed
- no sensitive logs published

---

# Deployment Pipeline

```text
GitHub Actions Cron
        ↓
Install Dependencies
        ↓
Run Dashboard Script
        ↓
Generate Charts & HTML
        ↓
Publish Output
        ↓
GitHub Pages Deployment
```

---

# GitHub Actions Workflow

Workflow file:
```text
.github/workflows/dashboard.yml
```

Responsibilities:
- checkout repository
- install Python
- install dependencies
- execute dashboard build
- publish dashboard output

---

# Environment Variables

Secrets should NEVER be hardcoded.

Use GitHub Secrets:
- GMAIL_SENDER
- GMAIL_PASSWORD
- GMAIL_RECIPIENT

Access pattern:
```python
os.getenv("GMAIL_SENDER")
```

---

# Dependency Management

Dependencies stored in:
```text
requirements.txt
```

Recommended update process:
```bash
pip freeze > requirements.txt
```

---

# GitHub Pages Configuration

Recommended deployment source:
- branch: main
- folder: /output or /docs

Public URL:
```text
https://<github-user>.github.io/<repo-name>/
```

---

# Technical Indicator Deployment

Indicators such as RSI must:
- render correctly on mobile
- degrade gracefully if unavailable
- avoid breaking dashboard generation
- support missing-data scenarios

---

# Deployment Validation

After deployment verify:
- HTML loads successfully
- charts render correctly
- RSI section displays properly
- mobile layout works
- latest market data visible

---

# Logging & Monitoring

Primary log source:
- GitHub Actions logs

Recommended logging:
- execution duration
- failed tickers
- chart generation status
- indicator calculation status
- deployment timestamps

---

# Failure Recovery

## Dashboard Build Failure

Steps:
1. inspect GitHub Actions logs
2. verify dependencies
3. verify ticker downloads
4. verify indicator calculations

---

## Missing Charts

Check:
- chart output paths
- rendering backend
- file permissions

---

## GitHub Pages Not Updating

Check:
- deployment branch
- output directory
- workflow permissions

---

# Local Deployment Testing

Run locally before pushing:
```bash
python dashboard.py
```

Verify:
- output/index.html exists
- charts generated
- RSI section renders
- no console errors

---

# Recommended Git Workflow

## Feature Development
```bash
git checkout -b feature/add-rsi
```

## Commit
```bash
git commit -m "Add RSI indicator support"
```

## Push
```bash
git push origin feature/add-rsi
```

---

# Rollback Strategy

If deployment breaks:
1. revert last commit
2. rerun GitHub Action
3. verify dashboard restored

Rollback command:
```bash
git revert <commit-hash>
```

---

# Future Deployment Enhancements

Potential future upgrades:
- caching layer
- Docker deployment
- CDN caching
- deployment health checks
- staging dashboard
- alert notifications
```