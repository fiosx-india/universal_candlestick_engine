import numpy as np
import pandas as pd
import yfinance as yf

from constants import TIMEFRAMES, PATTERN_GROUPS
from historical.outcomes import forward_outcomes_all


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
    # Do NOT request a native 45m Yahoo interval.
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
# DATA LOADER
# ============================================================

def _download_data(symbol, timeframe, period=None):

    if timeframe not in TIMEFRAME_SETTINGS:
        raise ValueError(
            f"Unsupported timeframe: {timeframe}"
        )

    settings = TIMEFRAME_SETTINGS[timeframe]

    selected_period = (
        period
        if period is not None
        else settings["period"]
    )

    data = yf.download(
        symbol,
        period=selected_period,
        interval=settings["interval"],
        auto_adjust=False,
        progress=False,
    )

    if data is None or data.empty:
        raise ValueError(
            f"No market data available for {symbol} "
            f"at timeframe {timeframe}"
        )

    # Handle yfinance MultiIndex columns.
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = [
            column[0]
            for column in data.columns
        ]

    required = [
        "Open",
        "High",
        "Low",
        "Close",
    ]

    missing = [
        column
        for column in required
        if column not in data.columns
    ]

    if missing:
        raise ValueError(
            f"Missing OHLC columns: {missing}"
        )

    data = data.copy()

    for column in required:
        data[column] = pd.to_numeric(
            data[column],
            errors="coerce",
        )

    data.dropna(
        subset=required,
        inplace=True,
    )

    # ========================================================
    # BUILD THE REQUESTED TIMEFRAME
    # ========================================================

    data = _aggregate_ohlcv(
        data,
        timeframe,
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
    Convert base candles into the requested timeframe.

    Examples:
        1H  -> original 1H candles
        2H  -> 2 x 1H candles
        8H  -> 8 x 1H candles

        1D  -> original daily candles
        2D  -> 2 x daily candles
        15D -> 15 x daily candles

        1W  -> original weekly candles
        4W  -> 4 x weekly candles

        1M  -> original monthly candles
        12M -> 12 x monthly candles
    """

    if data is None or data.empty:
        return data

    # --------------------------------------------------------
    # Extract numeric multiplier
    # --------------------------------------------------------

    number = ""

    for char in timeframe:
        if char.isdigit():
            number += char
        else:
            break

    multiplier = int(number) if number else 1

    unit = timeframe[len(number):]

    # Base timeframe needs no aggregation
    if multiplier == 1:
        return data

    # --------------------------------------------------------
    # Select base group size
    # --------------------------------------------------------

    if unit == "H":
        base_unit = "H"

    elif unit == "D":
        base_unit = "D"

    elif unit == "W":
        base_unit = "W"

    elif unit == "M":
        base_unit = "M"

    else:
        return data

    # --------------------------------------------------------
    # OHLCV aggregation
    # --------------------------------------------------------

    aggregation = {
        "Open": "first",
        "High": "max",
        "Low": "min",
        "Close": "last",
    }

    if "Adj Close" in data.columns:
        aggregation["Adj Close"] = "last"

    if "Volume" in data.columns:
        aggregation["Volume"] = "sum"

    # --------------------------------------------------------
    # IMPORTANT:
    # Use sequential base candles.
    #
    # This prevents multi-day/month grouping from depending
    # on calendar boundaries and keeps the engine deterministic.
    # --------------------------------------------------------

    group_id = (
        np.arange(len(data))
        // multiplier
    )

    aggregated = (
        data.groupby(group_id, sort=True)
        .agg(aggregation)
    )

    # --------------------------------------------------------
    # Preserve the timestamp of the final base candle
    # in every aggregated candle.
    # --------------------------------------------------------

    last_indices = (
        data.groupby(group_id, sort=True)
        .apply(
            lambda x: x.index[-1],
            include_groups=False,
        )
    )

    aggregated.index = pd.DatetimeIndex(
        last_indices.values
    )

    aggregated.index.name = data.index.name

    return aggregated.dropna(
        subset=["Open", "High", "Low", "Close"]
    )

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
# PROBABILITY ENGINE
# ============================================================

def _calculate_probabilities(
    data,
    pattern_series,
):

    occurrence_indices = (
        _occurrence_indices(
            pattern_series
        )
    )

    if not occurrence_indices:
        return {}

    return forward_outcomes_all(
        df=data,
        occurrence_indices=occurrence_indices,
    )


# ============================================================
# MAIN ANALYSIS API
# ============================================================

def analyze(
    symbol,
    timeframe,
    period=None,
):

    if timeframe not in TIMEFRAMES:
        raise ValueError(
            f"Unsupported timeframe: {timeframe}"
        )

    data = _download_data(
        symbol,
        timeframe,
        period,
    )

    detected_patterns, all_patterns = (
        _build_patterns(data)
    )

    trend = _calculate_trend(
        data
    )

    volatility = _calculate_volatility(
        data
    )

    # --------------------------------------------------------
    # Current pattern probabilities
    # --------------------------------------------------------

    probabilities = {}

    for pattern_name in detected_patterns:

        series = all_patterns.get(
            pattern_name
        )

        if series is None:
            continue

        probabilities[
            pattern_name
        ] = _calculate_probabilities(
            data,
            series,
        )

    # --------------------------------------------------------
    # Projection
    # --------------------------------------------------------

    last_price = float(
        data["Close"].iloc[-1]
    )

    recent_high = float(
        data["High"].tail(20).max()
    )

    recent_low = float(
        data["Low"].tail(20).min()
    )

    projection_direction = trend

    projection = {
        "direction": projection_direction,
        "upper_zone": recent_high,
        "lower_zone": recent_low,
    }

    # --------------------------------------------------------
    # Final response
    # --------------------------------------------------------

    return {
        "symbol": symbol,
        "timeframe": timeframe,
        "data": data,
        "last_price": last_price,
        "trend": trend,
        "volatility": volatility,
        "patterns": detected_patterns,
        "probabilities": probabilities,
        "projection": projection,
        }
