#!/usr/bin/env python3
"""
WMA Dashboard Updater
=====================
Fetches OHLC data for all tickers, computes WMA 20/50/200,
injects data into wma_dashboard.html, generates per-ticker chart images,
and emails a summary to a Gmail account.

Cron: 30 17 * * 1-5   (5:30 PM every weekday)
"""

import json
import os
import re
import smtplib
import sys
import time
from datetime import datetime, date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from pathlib import Path

# ── Dependencies ────────────────────────────────────────────────────────────
try:
    import yfinance as yf
except ImportError:
    os.system(f"{sys.executable} -m pip install yfinance --quiet")
    import yfinance as yf

try:
    import pandas_datareader as pdr
except ImportError:
    os.system(f"{sys.executable} -m pip install pandas-datareader --quiet")
    import pandas_datareader as pdr

try:
    import requests
except ImportError:
    os.system(f"{sys.executable} -m pip install requests --quiet")
    import requests

try:
    import pandas as pd
except ImportError:
    os.system(f"{sys.executable} -m pip install pandas --quiet")
    import pandas as pd

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.patches import Patch
except ImportError:
    os.system(f"{sys.executable} -m pip install matplotlib --quiet")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.patches import Patch

# ── Configuration ───────────────────────────────────────────────────────────
# Edit these values before running

def get_base_path() -> Path:
    """Locate the repository path for config files.

    When running from stdin or an interactive shell, __file__ may not exist,
    so fall back to the current working directory.
    """
    try:
        return Path(__file__).resolve().parent
    except NameError:
        return Path.cwd()


def get_default_config() -> dict:
    base_path = get_base_path()
    return {
        # Tickers to track. BTC-USD maps to BTC in the dashboard.
        # Use "yfinance:" prefix for Yahoo Finance tickers, "fred:" for FRED sources
        "tickers": {
            "VOO":   "yfinance:VOO",
            "QQQM":  "yfinance:QQQM",
            "SMH":   "yfinance:SMH",
            "DRAM":  "yfinance:DRAM",
            "FBTC":  "yfinance:FBTC",
            "XLE":   "yfinance:XLE",
            "S&P 500": "yfinance:^GSPC",
            "TNX":   "yfinance:^TNX",
            "SK hynix": "yfinance:000660.KS",
            "Samsung Electronics": "yfinance:005930.KS",
            "Micron Technology": "yfinance:MU",
        },

        # Ticker overlays for comparison (plots multiple tickers on same chart)
        # Tickers are normalized to % change from first date for meaningful comparison
        "overlays": {
            "Tech vs Market": ["SPY", "QQQ"],
            "Commodities": ["GLD", "XLE"],
            "Semiconductor Leaders": ["Samsung Electronics", "SK hynix", "Micron Technology"],
            # "Bitcoin vs Stock Market": ["BTC", "SPY"],
        },

        # Start date for historical data (goes back to first available date for each ticker)
        # Yahoo Finance will return available data; not all tickers have data back to 1920
        "start_date": "1920-01-01",

        # Path to the HTML dashboard in the repository
        "html_path": base_path / "index.html",

        # Directory to save chart images temporarily in the repository
        "chart_dir": base_path / "charts",

        # ── Gmail settings ───────────────────────────────────────────────────────
        # Use an App Password (not your regular password):
        # Google Account → Security → 2-Step Verification → App Passwords
        "gmail_sender":   os.getenv("GMAIL_SENDER"),
        "gmail_password": os.getenv("GMAIL_PASSWORD"),
        "gmail_recipient": os.getenv("GMAIL_RECIPIENT"),     # ← CHANGE

        # Send email only on weekdays (Monday=0 … Friday=4)
        "send_email": True
    }

CONFIG = get_default_config()
# WMA periods to compute
WMA_PERIODS = [20, 50, 200]


def email_config_is_valid(config: dict) -> bool:
    """Return True if required Gmail config values are present."""
    missing = [name for name in ("gmail_sender", "gmail_password", "gmail_recipient") if not config.get(name)]
    if missing:
        print(f"  ✗ Email config missing: {', '.join(missing)}")
        print("    → Set GMAIL_SENDER, GMAIL_PASSWORD, and GMAIL_RECIPIENT in your environment or GitHub secrets.")
        return False
    return True

# ── Helper functions ─────────────────────────────────────────────────────────

def compute_wma(prices: list, period: int) -> list:
    """Compute Weighted Moving Average."""
    weights = list(range(1, period + 1))
    weight_sum = sum(weights)
    result = [None] * len(prices)
    for i in range(period - 1, len(prices)):
        val = sum(prices[i - period + 1 + j] * weights[j] for j in range(period))
        result[i] = round(val / weight_sum, 4)
    return result


def determine_signal(prices, wma20, wma50, wma200) -> str:
    """Return 'Bullish', 'Bearish', or 'Neutral' for the ticker."""
    if not prices:
        return "Neutral"
    p  = prices[-1]
    w20  = next((v for v in reversed(wma20)  if v is not None), None)
    w50  = next((v for v in reversed(wma50)  if v is not None), None)
    w200 = next((v for v in reversed(wma200) if v is not None), None)

    score = 0
    if w20  and p > w20:  score += 1
    if w50  and p > w50:  score += 1
    if w200 and p > w200: score += 1
    if w20 and w50 and w20 > w50: score += 1

    if score >= 4:  return "🟢 Bullish"
    if score <= 1:  return "🔴 Bearish"
    return "🟡 Neutral"


def fetch_data(tickers: dict, start: str) -> dict:
    """Download OHLC data from Yahoo Finance or FRED."""
    print(f"[{datetime.now():%H:%M:%S}] Fetching data from Yahoo Finance and FRED…")
    chart_data = {}
    
    for label, source_ticker in tickers.items():
        try:
            if source_ticker.startswith("fred:"):
                # Fetch from FRED (Federal Reserve Economic Data) using JSON API with retry logic
                fred_code = source_ticker.replace("fred:", "")
                max_retries = 3
                retry_delay = 2
                df = None
                
                for attempt in range(max_retries):
                    try:
                        # Use FRED JSON API with full observations
                        fred_url = f"https://api.fred.stlouisfed.org/series/data"
                        params = {
                            'series_id': fred_code,
                            'api_key': 'a3c0f3b0c1c2c3c4c5c6c7c8c9c0c1c2',  # FRED public API key
                            'file_type': 'json',
                            'limit': 120000
                        }
                        resp = requests.get(fred_url, params=params, timeout=60)
                        resp.raise_for_status()
                        data_json = resp.json()
                        
                        if 'observations' in data_json and data_json['observations']:
                            dates = []
                            values = []
                            start_dt = pd.to_datetime(start)
                            
                            for obs in data_json['observations']:
                                obs_date = pd.to_datetime(obs['date'])
                                if obs_date >= start_dt and obs['value'] != '.':
                                    try:
                                        dates.append(obs_date)
                                        values.append(float(obs['value']))
                                    except (ValueError, TypeError):
                                        continue
                            
                            if dates and values:
                                df = pd.DataFrame({'value': values}, index=dates)
                                break
                    except Exception as retry_e:
                        if attempt < max_retries - 1:
                            print(f"  ⚠ {label} attempt {attempt + 1}/{max_retries} failed, retrying in {retry_delay}s…")
                            time.sleep(retry_delay)
                            retry_delay *= 2  # Exponential backoff
                        else:
                            raise retry_e
                
                if df is None or df.empty:
                    print(f"  ⚠ No data for {label} ({fred_code})")
                    continue
                
                df = df.dropna()
                chart_data[label] = {
                    "dates": [str(d.date()) for d in df.index],
                    "open":  [round(float(v), 4) for v in df['value']],
                    "high":  [round(float(v), 4) for v in df['value']],
                    "low":   [round(float(v), 4) for v in df['value']],
                    "close": [round(float(v), 4) for v in df['value']],
                }
                print(f"  ✓ {label}: {len(df)} rows (FRED)")
            else:
                # Fetch from Yahoo Finance
                yf_ticker = source_ticker.replace("yfinance:", "")
                df = yf.download(yf_ticker, start=start, auto_adjust=True, progress=False)
                
                if df.empty:
                    print(f"  ⚠ No data for {label} ({yf_ticker})")
                    continue
                
                # Flatten MultiIndex columns if present
                if isinstance(df.columns, type(df.columns)) and hasattr(df.columns, 'levels'):
                    df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
                
                df = df.dropna(subset=["Close"])
                chart_data[label] = {
                    "dates": [str(d.date()) for d in df.index],
                    "open":  [round(float(v), 4) for v in df["Open"]],
                    "high":  [round(float(v), 4) for v in df["High"]],
                    "low":   [round(float(v), 4) for v in df["Low"]],
                    "close": [round(float(v), 4) for v in df["Close"]],
                }
                print(f"  ✓ {label}: {len(df)} rows (Yahoo Finance)")
        except Exception as e:
            print(f"  ✗ {label}: {e}")
        
        time.sleep(0.5)   # be polite to APIs
    
    return chart_data


def write_chart_json(chart_data: dict, json_path: Path):
    """Write the latest chart data to a JSON file for the dashboard to fetch."""
    payload = {
        "version": datetime.utcnow().isoformat() + "Z",
        "data": chart_data,
    }
    json_path.write_text(json.dumps(payload, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")
    print(f"[{datetime.now():%H:%M:%S}] Data JSON updated: {json_path}")


def embed_chart_data_in_html(chart_data: dict, html_path: Path):
    """Embed latest chart JSON into the HTML for local file-based viewing."""
    html = html_path.read_text(encoding="utf-8")
    json_str = json.dumps({"version": datetime.utcnow().isoformat() + "Z", "data": chart_data}, separators=(",", ":"), ensure_ascii=False)
    script_block = f'<script id="chart-data-json" type="application/json">{json_str}</script>'

    if 'id="chart-data-json"' in html:
        html = re.sub(
            r'<script\s+id="chart-data-json"[^>]*>.*?</script>',
            script_block,
            html,
            flags=re.DOTALL,
        )
    else:
        html = html.replace(
            "</div>\n\n<script>",
            f"</div>\n\n{script_block}\n\n<script>",
            1,
        )

    html_path.write_text(html, encoding="utf-8")
    print(f"[{datetime.now():%H:%M:%S}] Embedded chart data into HTML: {html_path}")


def generate_chart_image(label: str, data: dict, wma20, wma50, wma200, signal: str, out_path: Path):
    """Generate a matplotlib chart and save to disk."""
    import matplotlib.ticker
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from datetime import datetime as dt

    dates  = [dt.strptime(d, "%Y-%m-%d") for d in data["dates"]]
    closes = data["close"]

    fig, ax = plt.subplots(figsize=(12, 5))
    fig.patch.set_facecolor("#0d1117")
    ax.set_facecolor("#0d1117")

    ax.plot(dates, closes, color="#e6edf3", linewidth=1, label=f"{label} Close", zorder=3)

    # WMA lines
    valid_dates_20  = [d for d, v in zip(dates, wma20)  if v is not None]
    valid_dates_50  = [d for d, v in zip(dates, wma50)  if v is not None]
    valid_dates_200 = [d for d, v in zip(dates, wma200) if v is not None]
    vals_20  = [v for v in wma20  if v is not None]
    vals_50  = [v for v in wma50  if v is not None]
    vals_200 = [v for v in wma200 if v is not None]

    if vals_20:  ax.plot(valid_dates_20,  vals_20,  color="#f0c040", linewidth=1.2, label="WMA 20")
    if vals_50:  ax.plot(valid_dates_50,  vals_50,  color="#58a6ff", linewidth=1.5, label="WMA 50")
    if vals_200: ax.plot(valid_dates_200, vals_200, color="#ff6b6b", linewidth=2.0, label="WMA 200")

    # Formatting
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    plt.xticks(rotation=45, color="#8b949e", fontsize=7)
    ax.yaxis.tick_right()
    plt.yticks(color="#8b949e", fontsize=8)
    ax.tick_params(colors="#30363d", which="both")
    for spine in ax.spines.values():
        spine.set_edgecolor("#30363d")
    ax.set_yscale("log")
    ax.yaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter())
    ax.yaxis.get_major_formatter().set_scientific(False)
    ax.grid(True, color="#21262d", linewidth=0.5, which="both")

    sig_color = "#3fb950" if "Bullish" in signal else ("#f85149" if "Bearish" in signal else "#f0c040")
    ax.set_title(f"{label}  —  {signal}", color=sig_color, fontsize=13, fontweight="bold", pad=12)
    ax.legend(loc="upper left", fontsize=8, facecolor="#161b22", edgecolor="#30363d", labelcolor="#e6edf3")

    plt.tight_layout()
    fig.savefig(out_path, dpi=120, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


def generate_overlay_chart(overlay_name: str, ticker_labels: list, chart_data: dict, out_path: Path):
    """Generate a chart overlaying multiple tickers (normalized to % change)."""
    import matplotlib.ticker
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from datetime import datetime as dt

    # Color palette for overlay tickers
    colors = ["#58a6ff", "#f0c040", "#ff6b6b", "#3fb950", "#d29922", "#db61a2"]
    
    fig, ax = plt.subplots(figsize=(12, 5))
    fig.patch.set_facecolor("#0d1117")
    ax.set_facecolor("#0d1117")

    # Plot each ticker normalized to % change
    for idx, label in enumerate(ticker_labels):
        if label not in chart_data:
            continue
        
        data = chart_data[label]
        dates = [dt.strptime(d, "%Y-%m-%d") for d in data["dates"]]
        closes = data["close"]
        
        # Normalize to % change from first value
        first_price = closes[0]
        pct_changes = [(p / first_price - 1) * 100 for p in closes]
        
        color = colors[idx % len(colors)]
        ax.plot(dates, pct_changes, color=color, linewidth=2, label=label, zorder=3)

    # Formatting
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    plt.xticks(rotation=45, color="#8b949e", fontsize=7)
    ax.yaxis.tick_right()
    plt.yticks(color="#8b949e", fontsize=8)
    ax.tick_params(colors="#30363d", which="both")
    for spine in ax.spines.values():
        spine.set_edgecolor("#30363d")
    ax.grid(True, color="#21262d", linewidth=0.5, which="both")
    
    # Format y-axis as percentage
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(xmax=1))
    
    ax.set_title(f"{overlay_name}  —  % Change from Start Date", color="#58a6ff", fontsize=13, fontweight="bold", pad=12)
    ax.set_ylabel("% Change", color="#8b949e", fontsize=10)
    ax.axhline(y=0, color="#30363d", linestyle="--", linewidth=0.8, alpha=0.5)
    ax.legend(loc="upper left", fontsize=8, facecolor="#161b22", edgecolor="#30363d", labelcolor="#e6edf3")

    plt.tight_layout()
    fig.savefig(out_path, dpi=120, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


def send_email(config: dict, signals: dict, chart_paths: dict):
    """Build and send an HTML summary email with embedded chart images."""
    print(f"[{datetime.now():%H:%M:%S}] Preparing email…")

    msg = MIMEMultipart("related")
    msg["Subject"] = f"📊 WMA Market Summary — {date.today():%B %d, %Y}"
    msg["From"]    = config["gmail_sender"]
    msg["To"]      = config["gmail_recipient"]

    # Build HTML body
    rows = ""
    for t, sig in signals.items():
        color = "#3fb950" if "Bullish" in sig else ("#f85149" if "Bearish" in sig else "#f0c040")
        rows += f"""
        <tr>
          <td style="padding:10px 16px;font-weight:600;color:#e6edf3;">{t}</td>
          <td style="padding:10px 16px;color:{color};font-weight:700;">{sig}</td>
        </tr>
        <tr>
          <td colspan="2" style="padding:4px 16px 16px;">
            <img src="cid:chart_{t}" style="width:100%;max-width:700px;border-radius:6px;" alt="{t} chart">
          </td>
        </tr>"""

    body_html = f"""
    <html><body style="background:#0d1117;font-family:'Segoe UI',sans-serif;color:#e6edf3;padding:24px;">
      <h2 style="color:#58a6ff;margin-bottom:4px;">📈 WMA Dashboard Summary</h2>
      <p style="color:#8b949e;margin-bottom:24px;">Generated: {datetime.now():%Y-%m-%d %H:%M} — WMA 20 / 50 / 200</p>
      <table style="border-collapse:collapse;width:100%;max-width:740px;background:#161b22;border-radius:8px;overflow:hidden;">
        <thead><tr style="background:#21262d;">
          <th style="padding:12px 16px;text-align:left;color:#8b949e;">Ticker</th>
          <th style="padding:12px 16px;text-align:left;color:#8b949e;">Signal</th>
        </tr></thead>
        <tbody>{rows}</tbody>
      </table>
      <p style="color:#484f58;margin-top:24px;font-size:0.75rem;">This email was sent automatically by wma_updater.py via cron.</p>
    </body></html>"""

    msg.attach(MIMEText(body_html, "html"))

    # Attach chart images as inline
    for t, path in chart_paths.items():
        if path.exists():
            with open(path, "rb") as f:
                img = MIMEImage(f.read())
                img.add_header("Content-ID", f"<chart_{t}>")
                img.add_header("Content-Disposition", "inline", filename=path.name)
                msg.attach(img)

    if not email_config_is_valid(config):
        print("  ✗ Email skipped due to missing Gmail configuration.")
        return False

    # Send via Gmail SMTP
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(config["gmail_sender"], config["gmail_password"])
            server.sendmail(config["gmail_sender"], config["gmail_recipient"], msg.as_string())
        print(f"  ✓ Email sent to {config['gmail_recipient']}")
        return True
    except Exception as e:
        print(f"  ✗ Email failed: {e}")
        print("    → Ensure you're using a Gmail App Password, not your regular password.")
        print("    → See: https://support.google.com/accounts/answer/185833")
        return False


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    config = globals().get("CONFIG")
    if config is None:
        config = get_default_config()

    print(f"\n{'='*55}")
    print(f"  WMA Updater  —  {datetime.now():%Y-%m-%d %H:%M:%S}")
    print(f"{'='*55}\n")

    # 1. Fetch OHLC data
    chart_data = fetch_data(config["tickers"], config["start_date"])
    if not chart_data:
        print("No data fetched. Exiting.")
        sys.exit(1)

    # 2. Write fresh chart JSON so the webpage always fetches current data
    data_json_path = config["html_path"].parent / "chart_data.json"
    write_chart_json(chart_data, data_json_path)
    embed_chart_data_in_html(chart_data, config["html_path"])

    # 3. Compute WMAs + signals + generate chart images
    config["chart_dir"].mkdir(exist_ok=True)
    signals     = {}
    chart_paths = {}

    print(f"\n[{datetime.now():%H:%M:%S}] Computing WMAs and generating charts…")
    for label, data in chart_data.items():
        prices = data["close"]
        wma20  = compute_wma(prices, 20)
        wma50  = compute_wma(prices, 50)
        wma200 = compute_wma(prices, 200)
        sig    = determine_signal(prices, wma20, wma50, wma200)
        signals[label] = sig

        img_path = config["chart_dir"] / f"{label}.png"
        generate_chart_image(label, data, wma20, wma50, wma200, sig, img_path)
        chart_paths[label] = img_path
        print(f"  {label:6s} → {sig}")

    # 3.5 Generate overlay comparison charts
    if config.get("overlays"):
        print(f"\n[{datetime.now():%H:%M:%S}] Generating overlay charts…")
        for overlay_name, ticker_list in config["overlays"].items():
            # Check if all tickers in the overlay exist in fetched data
            valid_tickers = [t for t in ticker_list if t in chart_data]
            if valid_tickers:
                overlay_path = config["chart_dir"] / f"overlay_{overlay_name.replace(' ', '_')}.png"
                generate_overlay_chart(overlay_name, valid_tickers, chart_data, overlay_path)
                print(f"  {overlay_name:25s} → {overlay_path.name}")

    # 4. Send email (weekdays only, if enabled)
    if config["send_email"]:
        today = date.today().weekday()   # Mon=0 … Sun=6
        if today < 5:
            if not send_email(config, signals, chart_paths):
                print(f"\n[{datetime.now():%H:%M:%S}] Email was not sent.")
        else:
            print(f"\n[{datetime.now():%H:%M:%S}] Weekend — email skipped.")
    else:
        print(f"\n[{datetime.now():%H:%M:%S}] Email disabled in config.")

    print(f"\n[{datetime.now():%H:%M:%S}] Done ✓\n")


if __name__ == "__main__":
    main()








