import os
import re
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

from constants import TIMEFRAMES, PATTERN_GROUPS
from data.angel_one import AngelOneDataClient


# ============================================================
# CANONICAL TIMEFRAME NORMALIZATION
# ============================================================

def _normalize_timeframe(value):
    """
    Normalize timeframe names without confusing minutes ('m')
    with months ('M').

    Canonical forms:
        minute: 1m, 5m, 15m, 30m, 45m
        hour:   1H ... 8H
        day:    1D ... 15D
        week:   1W ... 4W
        month:  1M ... 12M
    """
    raw = str(value or "").strip()

    if not raw:
        raise ValueError("Timeframe cannot be empty.")

    compact = raw.replace(" ", "")

    minute_match = re.fullmatch(
        r"(\d+)(m|min|mins|minute|minutes)",
        compact,
    )
    if minute_match is None:
        # Accept textual minute aliases case-insensitively, but
        # never reinterpret uppercase "M" (month) as minute.
        textual = re.fullmatch(
            r"(\d+)(min|mins|minute|minutes)",
            compact,
            re.IGNORECASE,
        )
        minute_match = textual
    if minute_match:
        candidate = f"{int(minute_match.group(1))}m"
        if candidate in TIMEFRAME_SETTINGS:
            return candidate

    upper = compact.upper()

    if upper in {"60M", "60MIN", "1HR", "1HOUR"}:
        return "1H"

    if upper in {"1MO", "1MONTH"}:
        return "1M"

    if upper in TIMEFRAME_SETTINGS:
        return upper

    raise ValueError(f"Unsupported timeframe: {value}")


# ============================================================
# TIMEFRAME DATA SETTINGS
# ============================================================

TIMEFRAME_SETTINGS = {
    # --------------------------------------------------------
    # Intraday base timeframes
    # --------------------------------------------------------
    "1m": {
        "interval": "1m",
        "period": "7d",
        "base_timeframe": "1m",
        "multiplier": 1,
    },

    "5m": {
        "interval": "5m",
        "period": "60d",
        "base_timeframe": "5m",
        "multiplier": 1,
    },

    "15m": {
        "interval": "15m",
        "period": "60d",
        "base_timeframe": "15m",
        "multiplier": 1,
    },

    "30m": {
        "interval": "30m",
        "period": "60d",
        "base_timeframe": "30m",
        "multiplier": 1,
    },

    # 45m is built from 15m candles.
    # Angel One does not provide a native 45m interval; build it from 15m.
    "45m": {
        "interval": "15m",
        "period": "60d",
        "base_timeframe": "15m",
        "multiplier": 3,
    },

    # --------------------------------------------------------
    # Hourly timeframes
    # 2H-8H are constructed from 1H candles.
    # --------------------------------------------------------
    "1H": {
        "interval": "1h",
        "period": "2y",
        "base_timeframe": "1H",
        "multiplier": 1,
    },

    "2H": {
        "interval": "1h",
        "period": "2y",
        "base_timeframe": "1H",
        "multiplier": 2,
    },

    "3H": {
        "interval": "1h",
        "period": "2y",
        "base_timeframe": "1H",
        "multiplier": 3,
    },

    "4H": {
        "interval": "1h",
        "period": "2y",
        "base_timeframe": "1H",
        "multiplier": 4,
    },

    "5H": {
        "interval": "1h",
        "period": "2y",
        "base_timeframe": "1H",
        "multiplier": 5,
    },

    "6H": {
        "interval": "1h",
        "period": "2y",
        "base_timeframe": "1H",
        "multiplier": 6,
    },

    "7H": {
        "interval": "1h",
        "period": "2y",
        "base_timeframe": "1H",
        "multiplier": 7,
    },

    "8H": {
        "interval": "1h",
        "period": "2y",
        "base_timeframe": "1H",
        "multiplier": 8,
    },

    # --------------------------------------------------------
    # Daily timeframes
    # --------------------------------------------------------
    "1D": {
        "interval": "1d",
        "period": "5y",
        "base_timeframe": "1D",
        "multiplier": 1,
    },

    "2D": {
        "interval": "1d",
        "period": "5y",
        "base_timeframe": "1D",
        "multiplier": 2,
    },

    "3D": {
        "interval": "1d",
        "period": "5y",
        "base_timeframe": "1D",
        "multiplier": 3,
    },

    "4D": {
        "interval": "1d",
        "period": "5y",
        "base_timeframe": "1D",
        "multiplier": 4,
    },

    "5D": {
        "interval": "1d",
        "period": "5y",
        "base_timeframe": "1D",
        "multiplier": 5,
    },

    "6D": {
        "interval": "1d",
        "period": "5y",
        "base_timeframe": "1D",
        "multiplier": 6,
    },

    "7D": {
        "interval": "1d",
        "period": "5y",
        "base_timeframe": "1D",
        "multiplier": 7,
    },

    "10D": {
        "interval": "1d",
        "period": "5y",
        "base_timeframe": "1D",
        "multiplier": 10,
    },

    "15D": {
        "interval": "1d",
        "period": "5y",
        "base_timeframe": "1D",
        "multiplier": 15,
    },

    # --------------------------------------------------------
    # Weekly timeframes
    # --------------------------------------------------------
    "1W": {
        "interval": "1wk",
        "period": "10y",
        "base_timeframe": "1W",
        "multiplier": 1,
    },

    "2W": {
        "interval": "1wk",
        "period": "10y",
        "base_timeframe": "1W",
        "multiplier": 2,
    },

    "3W": {
        "interval": "1wk",
        "period": "10y",
        "base_timeframe": "1W",
        "multiplier": 3,
    },

    "4W": {
        "interval": "1wk",
        "period": "10y",
        "base_timeframe": "1W",
        "multiplier": 4,
    },

    # --------------------------------------------------------
    # Monthly timeframes
    # --------------------------------------------------------
    "1M": {
        "interval": "1mo",
        "period": "10y",
        "base_timeframe": "1M",
        "multiplier": 1,
    },

    "2M": {
        "interval": "1mo",
        "period": "10y",
        "base_timeframe": "1M",
        "multiplier": 2,
    },

    "3M": {
        "interval": "1mo",
        "period": "10y",
        "base_timeframe": "1M",
        "multiplier": 3,
    },

    "4M": {
        "interval": "1mo",
        "period": "10y",
        "base_timeframe": "1M",
        "multiplier": 4,
    },

    "5M": {
        "interval": "1mo",
        "period": "10y",
        "base_timeframe": "1M",
        "multiplier": 5,
    },

    "6M": {
        "interval": "1mo",
        "period": "10y",
        "base_timeframe": "1M",
        "multiplier": 6,
    },

    "7M": {
        "interval": "1mo",
        "period": "10y",
        "base_timeframe": "1M",
        "multiplier": 7,
    },

    "8M": {
        "interval": "1mo",
        "period": "10y",
        "base_timeframe": "1M",
        "multiplier": 8,
    },

    "9M": {
        "interval": "1mo",
        "period": "10y",
        "base_timeframe": "1M",
        "multiplier": 9,
    },

    "10M": {
        "interval": "1mo",
        "period": "10y",
        "base_timeframe": "1M",
        "multiplier": 10,
    },

    "11M": {
        "interval": "1mo",
        "period": "10y",
        "base_timeframe": "1M",
        "multiplier": 11,
    },

    "12M": {
        "interval": "1mo",
        "period": "10y",
        "base_timeframe": "1M",
        "multiplier": 12,
    },
}

# ============================================================
# ANGEL ONE CREDENTIALS
# ============================================================

def _get_secret(name):
    """
    Read a secret safely.

    Priority:
        1. Streamlit secrets
        2. Environment variable

    No credentials are hard-coded in source code.
    """

    # Streamlit Cloud / local Streamlit secrets
    try:
        import streamlit as st

        value = st.secrets.get(name)

        if value:
            return str(value).strip()

    except Exception:
        pass

    # Environment variable fallback
    value = os.getenv(name)

    if value:
        return str(value).strip()

    return ""


# ============================================================
# ANGEL ONE CLIENT
# ============================================================

_ANGEL_CLIENT = None


def _get_angel_client():
    """
    Create and cache one Angel One historical-data client.
    """

    global _ANGEL_CLIENT

    if _ANGEL_CLIENT is not None:
        return _ANGEL_CLIENT

    api_key = _get_secret("ANGEL_API_KEY")
    client_code = _get_secret("ANGEL_CLIENT_CODE")
    mpin = _get_secret("ANGEL_MPIN")
    totp_secret = _get_secret("ANGEL_TOTP_SECRET")

    missing = []

    if not api_key:
        missing.append("ANGEL_API_KEY")

    if not client_code:
        missing.append("ANGEL_CLIENT_CODE")

    if not mpin:
        missing.append("ANGEL_MPIN")

    if not totp_secret:
        missing.append("ANGEL_TOTP_SECRET")

    if missing:
        raise RuntimeError(
            "Angel One credentials are missing: "
            + ", ".join(missing)
        )

    _ANGEL_CLIENT = AngelOneDataClient(
        api_key=api_key,
        client_code=client_code,
        mpin=mpin,
        totp_secret=totp_secret,
    )

    return _ANGEL_CLIENT

# ============================================================
# SYMBOL / EXCHANGE RESOLUTION
# ============================================================

# Known index symbols
INDEX_EXCHANGE_MAP = {
    "NIFTY": "NSE",
    "NIFTY50": "NSE",
    "BANKNIFTY": "NSE",
    "FINNIFTY": "NSE",
    "MIDCPNIFTY": "NSE",

    "SENSEX": "BSE",
    "BANKEX": "BSE",
}

# Known commodity symbols
COMMODITY_EXCHANGE_MAP = {
    "GOLD": "MCX",
    "GOLDM": "MCX",
    "SILVER": "MCX",
    "SILVERM": "MCX",
    "CRUDEOIL": "MCX",
    "CRUDEOILM": "MCX",
    "NATURALGAS": "MCX",
    "NATURALGASM": "MCX",
    "COPPER": "MCX",
    "ZINC": "MCX",
    "ALUMINIUM": "MCX",
    "LEAD": "MCX",
    "NICKEL": "MCX",
}


def _resolve_exchange(symbol):
    """
    Resolve the correct Angel One exchange segment.

    Examples:
        RELIANCE.NS -> NSE
        RELIANCE.BO -> BSE
        NIFTY       -> NSE
        SENSEX      -> BSE
        GOLD        -> MCX
        CRUDEOIL    -> MCX
    """

    value = str(symbol).strip().upper()

    # Explicit Yahoo-style suffixes
    if value.endswith(".NS"):
        return "NSE"

    if value.endswith(".BO"):
        return "BSE"

    # Known indices
    if value in INDEX_EXCHANGE_MAP:
        return INDEX_EXCHANGE_MAP[value]

    # Known commodities
    if value in COMMODITY_EXCHANGE_MAP:
        return COMMODITY_EXCHANGE_MAP[value]

    # Normal equity default
    return "NSE"


def _resolve_angel_symbol(symbol):
    """
    Convert Yahoo-style symbols into Angel One searchable symbols.
    """

    value = str(symbol).strip().upper()

    if value.endswith(".NS"):
        return value[:-3]

    if value.endswith(".BO"):
        return value[:-3]

    return value


# ============================================================
# PERIOD -> DATE RANGE
# ============================================================

def _period_to_days(period):
    """
    Convert common UI period values into a safe day count.
    """

    if period is None:
        return 365

    value = str(period).strip().lower()

    match = re.fullmatch(
        r"(\d+)\s*([dwmy])",
        value,
    )

    if not match:
        return 365

    number = int(match.group(1))
    unit = match.group(2)

    if unit == "d":
        return number

    if unit == "w":
        return number * 7

    if unit == "m":
        return number * 30

    if unit == "y":
        return number * 365

    return 365


# ============================================================
# ANGEL ONE HISTORICAL DATA DOWNLOAD
# ============================================================

def _download_angel_data(
    symbol,
    timeframe,
    period=None,
    exchange=None,
    symboltoken=None,
):
    """
    Download normalized OHLCV data from Angel One.

    This is the ONLY market-data download path used by
    api/service.py.
    """

    timeframe = _normalize_timeframe(timeframe)

    if timeframe not in TIMEFRAME_SETTINGS:
        raise ValueError(
            f"Unsupported timeframe: {timeframe}"
        )

    settings = TIMEFRAME_SETTINGS[
        timeframe
    ]

    angel_interval = settings[
        "base_timeframe"
    ]

    # Angel One native interval names used by
    # data/angel_one.py
    interval_map = {
        "1m": "1m",
        "5m": "5m",
        "15m": "15m",
        "30m": "30m",
        "1H": "1H",
        "1D": "1D",
    }

    # --------------------------------------------------------
    # For derived timeframes, download the base timeframe.
    #
    # Examples:
    # 45m -> 15m
    # 2H  -> 1H
    # 8H  -> 1H
    # 2D  -> 1D
    # 15D -> 1D
    # --------------------------------------------------------

    if angel_interval not in interval_map:
        raise ValueError(
            f"Angel One base timeframe is not supported: "
            f"{angel_interval}"
        )

    native_interval = interval_map[
        angel_interval
    ]

    selected_period = (
        period
        if period is not None
        else settings["period"]
    )

    days = _period_to_days(
        selected_period
    )

    end = datetime.now()

    start = (
        end
        - timedelta(days=days)
    )

    exchange = str(
        exchange or ""
    ).strip().upper()

    angel_symbol = str(
        symbol
    ).strip().upper()

    symboltoken = str(
        symboltoken or ""
    ).strip()

    if not exchange:
        raise ValueError(
            f"Missing exchange for {angel_symbol}"
        )

    if not symboltoken:
        raise ValueError(
            f"Missing symbol token for "
            f"{exchange}:{angel_symbol}"
        )

    client = _get_angel_client()

    data = client.get_historical_data(
        symbol=angel_symbol,
        symboltoken=symboltoken,
        interval=native_interval,
        start=start,
        end=end,
        exchange=exchange,
    )

    if data is None or data.empty:
        raise ValueError(
            f"Angel One returned no market data for "
            f"{symbol} | {timeframe}"
        )

    # --------------------------------------------------------
    # Standardize columns
    # --------------------------------------------------------

    data = data.copy()

    required = [
        "Open",
        "High",
        "Low",
        "Close",
    ]

    for column in required:
        if column not in data.columns:
            raise ValueError(
                f"Angel One data missing column: {column}"
            )

        data[column] = pd.to_numeric(
            data[column],
            errors="coerce",
        )

    if "Volume" in data.columns:
        data["Volume"] = pd.to_numeric(
            data["Volume"],
            errors="coerce",
        )

    data.dropna(
        subset=required,
        inplace=True,
    )

    data = data[
        ~data.index.duplicated(
            keep="last"
        )
    ]

    data = data.sort_index()

    return data


# ============================================================
# DATA LOADER
# ============================================================

def _download_data(
    symbol,
    timeframe,
    period=None,
    exchange=None,
    symboltoken=None,
):
    """
    Central market-data entry point.

    Yahoo Finance is intentionally NOT used here.
    """

    timeframe = _normalize_timeframe(timeframe)

    if timeframe not in TIMEFRAME_SETTINGS:
        raise ValueError(
            f"Unsupported timeframe: {timeframe}"
        )

    data = _download_angel_data(
        symbol=symbol,
        timeframe=timeframe,
        period=period,
        exchange=exchange,
        symboltoken=symboltoken,
    )

    if data is None or data.empty:
        raise ValueError(
            f"No market data available for "
            f"{symbol} at {timeframe}"
        )

    # --------------------------------------------------------
    # IMPORTANT:
    # Existing timeframe aggregation engine remains intact.
    # --------------------------------------------------------

    data = _aggregate_ohlcv(
        data,
        timeframe,
    )

    if data is None or data.empty:
        raise ValueError(
            f"No completed candles available for "
            f"{symbol} at {timeframe}"
        )

    if len(data) < 10:
        raise ValueError(
            "Not enough historical candles."
        )

    return data
    

# ============================================================
# OHLCV TIMEFRAME AGGREGATION ENGINE
# ============================================================

def _aggregate_ohlcv(data, timeframe):
    """
    Convert downloaded base candles into the requested timeframe.

    Minute aggregation is special:
        45m = 3 x 15m

    Other derived timeframes use the configured base-timeframe
    multiplier. Groups are intentionally sequential to preserve the
    project's existing custom-timeframe semantics.
    """

    if data is None or data.empty:
        return data

    timeframe = _normalize_timeframe(timeframe)

    settings = TIMEFRAME_SETTINGS.get(timeframe)
    if settings is None:
        raise ValueError(f"Unsupported timeframe: {timeframe}")

    multiplier = int(settings.get("multiplier", 1))

    if multiplier <= 1:
        return data.copy()

    frame = data.copy().sort_index()
    frame = frame[
        ~frame.index.duplicated(keep="last")
    ]

    if frame.empty:
        return frame

    required_columns = [
        "Open",
        "High",
        "Low",
        "Close",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in frame.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Cannot aggregate {timeframe}. "
            f"Missing columns: {missing_columns}"
        )

    aggregation = {
        "Open": "first",
        "High": "max",
        "Low": "min",
        "Close": "last",
    }

    if "Volume" in frame.columns:
        aggregation["Volume"] = "sum"

    if "Adj Close" in frame.columns:
        aggregation["Adj Close"] = "last"

    group_id = np.arange(len(frame)) // multiplier

    grouped = frame.groupby(
        group_id,
        sort=True,
        dropna=False,
    )

    # Only complete groups are valid historical candles.
    sizes = grouped.size()
    complete_groups = sizes.index[sizes == multiplier]

    if len(complete_groups) == 0:
        return frame.iloc[0:0].copy()

    aggregated = grouped.agg(aggregation).loc[
        complete_groups
    ]

    last_indices = grouped.apply(
        lambda x: x.index[-1],
        include_groups=False,
    ).loc[complete_groups]

    aggregated.index = pd.DatetimeIndex(
        last_indices.to_numpy()
    )
    aggregated.index.name = frame.index.name

    aggregated = aggregated.dropna(
        subset=required_columns
    ).sort_index()

    return aggregated


# ============================================================
# BASIC CANDLE CALCULATIONS
# ============================================================

def _candle_features(data):

    O = data["Open"]
    H = data["High"]
    L = data["Low"]
    C = data["Close"]

    body = (C - O).abs()

    candle_range = (
        H - L
    ).replace(0, np.nan)

    upper_shadow = (
        H - pd.concat([O, C], axis=1).max(axis=1)
    )

    lower_shadow = (
        pd.concat([O, C], axis=1).min(axis=1) - L
    )

    bullish = C > O
    bearish = C < O

    return (
        O,
        H,
        L,
        C,
        body,
        candle_range,
        upper_shadow,
        lower_shadow,
        bullish,
        bearish,
    )


# ============================================================
# CANDLESTICK PATTERNS
# ============================================================

def _detect_candlestick_patterns(data):

    (
        O,
        H,
        L,
        C,
        body,
        candle_range,
        upper_shadow,
        lower_shadow,
        bullish,
        bearish,
    ) = _candle_features(data)

    safe_range = candle_range.fillna(0)

    patterns = {}

    # --------------------------------------------------------
    # Doji
    # --------------------------------------------------------

    patterns["Doji"] = (
        body <= safe_range * 0.10
    )

    # --------------------------------------------------------
    # Hammer
    # --------------------------------------------------------

    patterns["Hammer"] = (
        (body <= safe_range * 0.35)
        & (lower_shadow >= body * 1.5)
        & (upper_shadow <= body * 0.75)
    )

    # --------------------------------------------------------
    # Shooting Star
    # --------------------------------------------------------

    patterns["Shooting Star"] = (
        (body <= safe_range * 0.35)
        & (upper_shadow >= body * 1.5)
        & (lower_shadow <= body * 0.75)
    )

    # --------------------------------------------------------
    # Bullish Engulfing
    # --------------------------------------------------------

    patterns["Bullish Engulfing"] = (
        bearish.shift(1)
        & bullish
        & (O <= C.shift(1))
        & (C >= O.shift(1))
    )

    # --------------------------------------------------------
    # Bearish Engulfing
    # --------------------------------------------------------

    patterns["Bearish Engulfing"] = (
        bullish.shift(1)
        & bearish
        & (O >= C.shift(1))
        & (C <= O.shift(1))
    )

    # --------------------------------------------------------
    # Bullish Marubozu
    # --------------------------------------------------------

    patterns["Bullish Marubozu"] = (
        bullish
        & (body >= safe_range * 0.90)
    )

    # --------------------------------------------------------
    # Bearish Marubozu
    # --------------------------------------------------------

    patterns["Bearish Marubozu"] = (
        bearish
        & (body >= safe_range * 0.90)
    )

    # --------------------------------------------------------
    # Inside Bar
    # --------------------------------------------------------

    patterns["Inside Bar"] = (
        (H < H.shift(1))
        & (L > L.shift(1))
    )

    # --------------------------------------------------------
    # Morning Star - simplified 3 candle structure
    # --------------------------------------------------------

    first_bear = bearish.shift(2)
    second_small = (
        body.shift(1)
        <= safe_range.shift(1) * 0.35
    )
    third_bull = bullish

    patterns["Morning Star"] = (
        first_bear
        & second_small
        & third_bull
        & (C >= (O.shift(2) + C.shift(2)) / 2)
    )

    # --------------------------------------------------------
    # Evening Star
    # --------------------------------------------------------

    first_bull = bullish.shift(2)
    third_bear = bearish

    patterns["Evening Star"] = (
        first_bull
        & second_small
        & third_bear
        & (C <= (O.shift(2) + C.shift(2)) / 2)
    )

    # --------------------------------------------------------
    # Three Line Strike
    # --------------------------------------------------------

    three_bull = (
        bullish.shift(3)
        & bullish.shift(2)
        & bullish.shift(1)
    )

    three_bear = (
        bearish.shift(3)
        & bearish.shift(2)
        & bearish.shift(1)
    )

    bullish_strike = (
        three_bear
        & bullish
        & (C > O.shift(3))
    )

    bearish_strike = (
        three_bull
        & bearish
        & (C < O.shift(3))
    )

    patterns["Three Line Strike"] = (
        bullish_strike
        | bearish_strike
    )

    return patterns


# ============================================================
# STRUCTURE PATTERNS
# ============================================================

def _detect_structure_patterns(data):

    C = data["Close"]

    result = {}

    rolling_low = C.rolling(5).min()
    rolling_high = C.rolling(5).max()

    # V reversal approximation
    result["V Reversal"] = (
        (C.shift(2) > C.shift(1))
        & (C > C.shift(1))
        & (
            C.shift(1)
            <= C.shift(2)
        )
    )

    # W pattern approximation
    result["W Pattern"] = (
        (C.shift(4) > C.shift(3))
        & (C.shift(2) < C.shift(3))
        & (C.shift(2) <= rolling_low.shift(2))
        & (C > C.shift(2))
    )

    # M pattern approximation
    result["M Pattern"] = (
        (C.shift(4) < C.shift(3))
        & (C.shift(2) > C.shift(3))
        & (C.shift(2) >= rolling_high.shift(2))
        & (C < C.shift(2))
    )

    return result


# ============================================================
# TREND
# ============================================================

def _calculate_trend(data):

    close = data["Close"]

    fast = close.rolling(20).mean()
    slow = close.rolling(50).mean()

    if len(close) < 50:
        return "NEUTRAL"

    if (
        fast.iloc[-1] > slow.iloc[-1]
        and close.iloc[-1] > fast.iloc[-1]
    ):
        return "BULLISH"

    if (
        fast.iloc[-1] < slow.iloc[-1]
        and close.iloc[-1] < fast.iloc[-1]
    ):
        return "BEARISH"

    return "SIDEWAYS"


# ============================================================
# VOLATILITY
# ============================================================

def _calculate_volatility(data):

    returns = data["Close"].pct_change()

    if returns.dropna().empty:
        return "LOW"

    volatility = float(
        returns.std()
    )

    if volatility >= 0.03:
        return "HIGH"

    if volatility >= 0.015:
        return "MEDIUM"

    return "LOW"


# ============================================================
# PATTERN OUTPUT
# ============================================================

def _build_patterns(data):

    candle_patterns = (
        _detect_candlestick_patterns(data)
    )

    structure_patterns = (
        _detect_structure_patterns(data)
    )

    all_patterns = {}

    all_patterns.update(
        candle_patterns
    )

    all_patterns.update(
        structure_patterns
    )

    detected = []

    for name, series in all_patterns.items():

        if bool(series.iloc[-1]):
            detected.append(name)

    return detected, all_patterns


# ============================================================
# HISTORICAL PATTERN OCCURRENCES
# ============================================================

def _occurrence_indices(series):

    if series is None:
        return []

    return list(
        series[
            series.fillna(False)
        ].index
    )


# ============================================================
# NEXT-BAR HISTORICAL EVIDENCE
# ============================================================

def _calculate_next_bar_outcome(
    data,
    pattern_series,
):
    """
    Calculate historical direction after the *next completed bar*.

    This deliberately uses one horizon only. The old implementation
    mixed 1H/2H/.../12M outcomes from the same occurrences into one
    probability, which double-counted evidence and made the displayed
    probability ambiguous.
    """

    occurrence_indices = _occurrence_indices(
        pattern_series
    )

    if not occurrence_indices:
        return None

    closes = pd.to_numeric(
        data["Close"],
        errors="coerce",
    )

    returns = []

    for idx in occurrence_indices:
        positions = data.index.get_indexer([idx])

        if len(positions) == 0:
            continue

        pos = int(positions[0])

        if pos < 0 or pos + 1 >= len(data):
            continue

        start = closes.iloc[pos]
        end = closes.iloc[pos + 1]

        if pd.isna(start) or pd.isna(end):
            continue

        start = float(start)
        end = float(end)

        if start <= 0:
            continue

        returns.append(
            (end / start) - 1.0
        )

    if not returns:
        return None

    arr = np.asarray(
        returns,
        dtype=float,
    )

    bullish = float(
        (arr > 0.002).mean()
    )
    bearish = float(
        (arr < -0.002).mean()
    )
    sideways = max(
        0.0,
        1.0 - bullish - bearish,
    )

    return {
        "samples": int(len(arr)),
        "bullish": bullish,
        "bearish": bearish,
        "sideways": sideways,
        "median_return": float(np.median(arr)),
        "mean_return": float(np.mean(arr)),
        "win_rate": float((arr > 0).mean()),
    }


# ============================================================
# CONTEXT / PROBABILITY HELPERS
# ============================================================

def _calculate_atr(data, window=14):
    high = pd.to_numeric(
        data["High"],
        errors="coerce",
    )
    low = pd.to_numeric(
        data["Low"],
        errors="coerce",
    )
    close = pd.to_numeric(
        data["Close"],
        errors="coerce",
    )

    previous_close = close.shift(1)

    tr = pd.concat(
        [
            high - low,
            (high - previous_close).abs(),
            (low - previous_close).abs(),
        ],
        axis=1,
    ).max(axis=1)

    atr = tr.rolling(
        window,
        min_periods=max(5, window // 2),
    ).mean()

    value = atr.iloc[-1]
    return (
        float(value)
        if pd.notna(value)
        else None
    )


def _trend_strength(data):
    """
    Return a bounded 0..1 directional context score.

    This is evidence strength, not a calibrated probability.
    """
    close = pd.to_numeric(
        data["Close"],
        errors="coerce",
    )

    if len(close) < 50:
        return 0.0

    fast = close.rolling(20).mean().iloc[-1]
    slow = close.rolling(50).mean().iloc[-1]

    if pd.isna(fast) or pd.isna(slow) or slow == 0:
        return 0.0

    spread = abs(float(fast / slow - 1.0))

    slope = 0.0
    if len(close) >= 10 and close.iloc[-10] != 0:
        slope = abs(
            float(
                close.iloc[-1]
                / close.iloc[-10]
                - 1.0
            )
        )

    strength = (
        min(spread / 0.02, 1.0) * 0.6
        + min(slope / 0.03, 1.0) * 0.4
    )

    return float(
        max(0.0, min(1.0, strength))
    )


def _build_probability_estimate(
    data,
    trend,
    patterns,
    historical_evidence,
):
    """
    Build a conservative evidence distribution.

    Priority:
        1. Historical next-bar evidence when available
        2. Current detected pattern evidence
        3. Trend context
        4. Neutral prior

    The output is an estimate, not a calibrated guarantee.
    """

    probabilities = {
        "bullish": 1.0 / 3.0,
        "bearish": 1.0 / 3.0,
        "sideways": 1.0 / 3.0,
    }

    # Historical evidence gets the strongest weight when enough
    # samples exist. Small samples are deliberately shrunk toward
    # the neutral prior.
    if historical_evidence:
        samples = int(
            historical_evidence.get("samples", 0)
        )

        if samples > 0:
            confidence = min(
                0.65,
                samples / 50.0,
            )

            historical = {
                "bullish": float(
                    historical_evidence["bullish"]
                ),
                "bearish": float(
                    historical_evidence["bearish"]
                ),
                "sideways": float(
                    historical_evidence["sideways"]
                ),
            }

            for key in probabilities:
                probabilities[key] = (
                    (1.0 - confidence)
                    * probabilities[key]
                    + confidence
                    * historical[key]
                )

    # Pattern evidence is directional context.
    pattern_votes = {
        "bullish": 0.0,
        "bearish": 0.0,
        "sideways": 0.0,
    }

    for pattern in patterns:
        direction = str(
            pattern.direction
        ).lower()

        if direction in pattern_votes:
            pattern_votes[direction] += max(
                0.0,
                min(
                    1.0,
                    float(pattern.confidence),
                ),
            )

    vote_total = sum(
        pattern_votes.values()
    )

    if vote_total > 0:
        pattern_distribution = {
            key: pattern_votes[key] / vote_total
            for key in pattern_votes
        }

        for key in probabilities:
            probabilities[key] = (
                0.75 * probabilities[key]
                + 0.25 * pattern_distribution[key]
            )

    # Trend is context, not certainty.
    strength = _trend_strength(data)

    if trend == "BULLISH":
        probabilities["bullish"] += 0.12 * strength
        probabilities["bearish"] -= 0.06 * strength
    elif trend == "BEARISH":
        probabilities["bearish"] += 0.12 * strength
        probabilities["bullish"] -= 0.06 * strength

    probabilities = {
        key: max(
            0.0,
            float(value),
        )
        for key, value in probabilities.items()
    }

    total = sum(probabilities.values()) or 1.0

    return {
        key: value / total
        for key, value in probabilities.items()
    }


# ============================================================
# MAIN ANALYSIS API
# ============================================================

def analyze(
    instrument,
    timeframe,
    period=None,
):
    """
    Analyze one exact Angel One instrument.

    Backward compatibility:
        - Current UI passes the selected instrument dictionary.
        - Older callers may pass a symbol string; that path resolves
          the instrument through Angel One before downloading data.
    """

    # --------------------------------------------------------
    # Resolve instrument
    # --------------------------------------------------------

    if isinstance(instrument, dict):
        selected = instrument.copy()
    elif isinstance(instrument, str):
        requested = instrument.strip().upper()

        if not requested:
            raise ValueError("Instrument symbol cannot be empty.")

        if requested.endswith(".BO"):
            exchange = "BSE"
        else:
            exchange = "NSE"

        client = _get_angel_client()
        selected = client.resolve_instrument(
            exchange=exchange,
            query=requested,
        )
    else:
        raise TypeError(
            "instrument must be an Angel One instrument dictionary "
            "or a symbol string."
        )

    exchange = str(
        selected.get("exchange", "")
    ).strip().upper()

    symbol = str(
        selected.get("tradingsymbol", "")
    ).strip().upper()

    symboltoken = str(
        selected.get("symboltoken", "")
    ).strip()

    if not exchange:
        raise ValueError(
            "Selected instrument is missing exchange."
        )

    if not symbol:
        raise ValueError(
            "Selected instrument is missing tradingsymbol."
        )

    if not symboltoken:
        raise ValueError(
            f"Selected instrument is missing symboltoken "
            f"for {exchange}:{symbol}"
        )

    # --------------------------------------------------------
    # Canonical timeframe
    # --------------------------------------------------------

    timeframe = _normalize_timeframe(timeframe)

    if timeframe not in TIMEFRAMES:
        raise ValueError(
            f"Unsupported timeframe: {timeframe}"
        )

    # --------------------------------------------------------
    # Download exact Angel One instrument data
    # --------------------------------------------------------

    data = _download_data(
        symbol=symbol,
        timeframe=timeframe,
        period=period,
        exchange=exchange,
        symboltoken=symboltoken,
    )

    if data is None or data.empty:
        raise ValueError(
            f"No market data available for "
            f"{exchange}:{symbol} | "
            f"Token {symboltoken} | "
            f"{timeframe}"
        )

    # --------------------------------------------------------
    # Candle + structure detection
    # --------------------------------------------------------

    detected_names, all_patterns = _build_patterns(data)

    from models import PatternResult

    pattern_metadata = {
        "Doji": ("SIDEWAYS", "CONFIRMED", 0.60),
        "Hammer": ("BULLISH", "CONFIRMED", 0.72),
        "Shooting Star": ("BEARISH", "CONFIRMED", 0.72),
        "Bullish Engulfing": ("BULLISH", "CONFIRMED", 0.82),
        "Bearish Engulfing": ("BEARISH", "CONFIRMED", 0.82),
        "Bullish Marubozu": ("BULLISH", "CONFIRMED", 0.76),
        "Bearish Marubozu": ("BEARISH", "CONFIRMED", 0.76),
        "Inside Bar": ("SIDEWAYS", "CONFIRMED", 0.64),
        "Morning Star": ("BULLISH", "CONFIRMED", 0.75),
        "Evening Star": ("BEARISH", "CONFIRMED", 0.75),
        "Three Line Strike": ("SIDEWAYS", "CONFIRMED", 0.64),
        "V Reversal": ("BULLISH", "FORMING", 0.65),
        "W Pattern": ("BULLISH", "FORMING", 0.68),
        "M Pattern": ("BEARISH", "FORMING", 0.68),
    }

    patterns = []

    for name in detected_names:
        direction, state, confidence = pattern_metadata.get(
            name,
            ("SIDEWAYS", "FORMING", 0.50),
        )

        patterns.append(
            PatternResult(
                name=name,
                direction=direction,
                state=state,
                confidence=confidence,
                score=confidence,
                timeframe=timeframe,
                details={
                    "source": "api.service",
                    "exchange": exchange,
                    "symboltoken": symboltoken,
                },
            )
        )

    # --------------------------------------------------------
    # Trend / volatility
    # --------------------------------------------------------

    trend = _calculate_trend(data)
    volatility = _calculate_volatility(data)

    # --------------------------------------------------------
    # Historical next-bar evidence
    #
    # IMPORTANT:
    # Only one horizon is blended into the current probability.
    # The old code summed every horizon from 1H through 12M,
    # which counted the same historical occurrence repeatedly.
    # --------------------------------------------------------

    historical_evidence = None

    for pattern_name in detected_names:
        series = all_patterns.get(pattern_name)

        if series is None:
            continue

        outcome = _calculate_next_bar_outcome(
            data,
            series,
        )

        if not outcome:
            continue

        if historical_evidence is None:
            historical_evidence = {
                "samples": 0,
                "bullish": 0.0,
                "bearish": 0.0,
                "sideways": 0.0,
            }

        samples = int(
            outcome["samples"]
        )

        historical_evidence["samples"] += samples
        historical_evidence["bullish"] += (
            outcome["bullish"] * samples
        )
        historical_evidence["bearish"] += (
            outcome["bearish"] * samples
        )
        historical_evidence["sideways"] += (
            outcome["sideways"] * samples
        )

    if historical_evidence:
        samples = historical_evidence["samples"]

        if samples > 0:
            historical_evidence["bullish"] /= samples
            historical_evidence["bearish"] /= samples
            historical_evidence["sideways"] /= samples

    probabilities = _build_probability_estimate(
        data=data,
        trend=trend,
        patterns=patterns,
        historical_evidence=historical_evidence,
    )

    # --------------------------------------------------------
    # Confluence = evidence strength, NOT probability.
    # --------------------------------------------------------

    if patterns:
        pattern_confidence = float(
            np.mean([
                float(p.confidence)
                for p in patterns
            ])
        )
    else:
        pattern_confidence = 0.0

    historical_strength = 0.0

    if historical_evidence:
        historical_strength = min(
            1.0,
            historical_evidence["samples"] / 50.0,
        )

    trend_strength = _trend_strength(data)

    confluence = (
        0.40 * pattern_confidence
        + 0.35 * historical_strength
        + 0.25 * trend_strength
    )

    # --------------------------------------------------------
    # ATR-based projection zone
    # --------------------------------------------------------

    last_price = float(
        data["Close"].iloc[-1]
    )

    atr = _calculate_atr(data)

    if atr is None or atr <= 0:
        atr = max(
            last_price * 0.01,
            1e-8,
        )

    edge = (
        probabilities["bullish"]
        - probabilities["bearish"]
    )

    if edge > 0.08:
        projection_direction = "BULLISH"
    elif edge < -0.08:
        projection_direction = "BEARISH"
    else:
        projection_direction = "SIDEWAYS"

    projection = {
        "direction": projection_direction,
        "upper_zone": last_price + atr,
        "lower_zone": max(
            0.0,
            last_price - atr,
        ),
        "atr": atr,
        "edge": edge,
    }

    # --------------------------------------------------------
    # Final response
    # --------------------------------------------------------

    return {
        "symbol": symbol,
        "exchange": exchange,
        "symboltoken": symboltoken,
        "timeframe": timeframe,
        "data": data,
        "last_price": last_price,
        "trend": trend,
        "volatility": volatility,
        "patterns": patterns,
        "probabilities": probabilities,
        "projection": projection,
        "historical_samples": (
            int(
                historical_evidence["samples"]
            )
            if historical_evidence
            else 0
        ),
        "historical_evidence": (
            {
                "bullish": historical_evidence["bullish"],
                "bearish": historical_evidence["bearish"],
                "sideways": historical_evidence["sideways"],
                "samples": historical_evidence["samples"],
            }
            if historical_evidence
            else None
        ),
        "confluence": confluence,
    }

