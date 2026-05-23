import math

import pandas as pd


def _coerce_numeric_series(values):
    if values is None:
        return pd.Series(dtype=float)

    series = pd.Series(values, dtype=float)
    return series


def _round_or_none(value):
    if value is None:
        return None

    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None

    if not math.isfinite(numeric):
        return None

    return round(numeric, 4)


def _safe_last(series):
    if series is None or series.empty:
        return None

    last_valid = series.dropna()
    if last_valid.empty:
        return None

    return _round_or_none(last_valid.iloc[-1])


def compute_macd_summary(close_series, fast=12, slow=26, signal=9):
    series = _coerce_numeric_series(close_series)
    if series.empty:
        return {"macd": None, "signal": None, "histogram": None, "trend": "N/A"}

    if len(series) < slow:
        return {"macd": None, "signal": None, "histogram": None, "trend": "N/A"}

    fast_ema = series.ewm(span=fast, adjust=False).mean()
    slow_ema = series.ewm(span=slow, adjust=False).mean()
    macd = fast_ema - slow_ema
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    histogram = macd - signal_line

    macd_value = _safe_last(macd)
    signal_value = _safe_last(signal_line)
    histogram_value = _safe_last(histogram)

    if macd_value is None or signal_value is None:
        trend = "N/A"
    elif macd_value > signal_value:
        trend = "Bullish"
    elif macd_value < signal_value:
        trend = "Bearish"
    else:
        trend = "Neutral"

    return {
        "macd": macd_value,
        "signal": signal_value,
        "histogram": histogram_value,
        "trend": trend,
    }


def compute_bollinger_summary(close_series, window=20, std_dev=2.0):
    series = _coerce_numeric_series(close_series)
    if series.empty:
        return {"upper": None, "middle": None, "lower": None}

    rolling_mean = series.rolling(window=window).mean()
    rolling_std = series.rolling(window=window).std(ddof=0)
    upper = rolling_mean + (std_dev * rolling_std)
    middle = rolling_mean
    lower = rolling_mean - (std_dev * rolling_std)

    return {
        "upper": _safe_last(upper),
        "middle": _safe_last(middle),
        "lower": _safe_last(lower),
    }


def compute_volume_trend_summary(volume_series, window=20):
    series = _coerce_numeric_series(volume_series)
    if series.empty or series.dropna().empty:
        return {"volume_ma": None, "volume_ratio": None, "label": "N/A", "current_volume": None}

    volume_ma = series.rolling(window=window).mean()
    current_volume = _safe_last(series)
    current_ma = _safe_last(volume_ma)

    if current_volume is None or current_ma is None or current_ma == 0:
        return {"volume_ma": current_ma, "volume_ratio": None, "label": "N/A", "current_volume": current_volume}

    ratio = round(current_volume / current_ma, 4)
    if ratio > 1.2:
        label = "Expanding"
    elif ratio < 0.8:
        label = "Contracting"
    else:
        label = "Normal"

    return {
        "volume_ma": current_ma,
        "volume_ratio": ratio,
        "label": label,
        "current_volume": current_volume,
    }


def compute_indicator_summary(close_series, volume_series):
    return {
        "macd": compute_macd_summary(close_series),
        "bollinger": compute_bollinger_summary(close_series),
        "volume": compute_volume_trend_summary(volume_series),
    }
