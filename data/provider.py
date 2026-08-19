# ============================================================
# MARKET DATA PROVIDER
# Yahoo Finance Safe Download Layer
# ============================================================

import random
import time

import pandas as pd
import yfinance as yf

from ..exceptions import DataError


# ============================================================
# SAFE YAHOO FINANCE DOWNLOAD
# ============================================================

def _safe_yf_download(
    symbol: str,
    period: str,
    interval: str,
    max_retries: int = 3,
) -> pd.DataFrame:
    """
    Safely download OHLCV market data from Yahoo Finance.

    Features:
        - Retry on temporary failures
        - Exponential backoff
        - Random jitter
        - No fake market data
        - Empty responses are treated as failures
        - Yahoo errors are converted into DataError
    """

    last_error = None

    for attempt in range(max_retries):
        try:
            df = yf.download(
                symbol,
                period=period,
                interval=interval,
                progress=False,
                auto_adjust=False,
                threads=False,
            )

            if df is not None and not df.empty:
                return df

        except Exception as exc:
            last_error = exc

        # ----------------------------------------------------
        # Wait before retrying.
        #
        # 1st retry  -> ~1.5–2.5 sec
        # 2nd retry  -> ~2.5–3.5 sec
        # ----------------------------------------------------

        if attempt < max_retries - 1:
            delay = (
                (2 ** attempt)
                + random.uniform(0.5, 1.5)
            )

            time.sleep(delay)

    # --------------------------------------------------------
    # All attempts failed
    # --------------------------------------------------------

    if last_error is not None:
        raise DataError(
            f"Yahoo Finance data request failed for "
            f"{symbol} / {interval} after "
            f"{max_retries} attempts: {last_error}"
        ) from last_error

    raise DataError(
        f"No market data returned for "
        f"{symbol} / {interval} after "
        f"{max_retries} attempts"
    )


# ============================================================
# PUBLIC OHLCV DATA PROVIDER
# ============================================================

def fetch_ohlcv(
    symbol: str,
    period: str = "2y",
    interval: str = "1d",
) -> pd.DataFrame:
    """
    Fetch normalized OHLCV market data.

    This is the single market-data gateway used by the
    Universal Candlestick Engine.

    Returns:
        pandas.DataFrame containing:

            Open
            High
            Low
            Close
            Volume

    Raises:
        DataError:
            If Yahoo Finance cannot provide valid data.
    """

    symbol = str(symbol).strip().upper()

    if not symbol:
        raise DataError(
            "Market symbol cannot be empty."
        )

    # --------------------------------------------------------
    # Download safely
    # --------------------------------------------------------

    df = _safe_yf_download(
        symbol=symbol,
        period=period,
        interval=interval,
        max_retries=3,
    )

    # --------------------------------------------------------
    # Normalize Yahoo MultiIndex columns
    # --------------------------------------------------------

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [
            column[0]
            if isinstance(column, tuple)
            else column
            for column in df.columns
        ]

    # --------------------------------------------------------
    # Required OHLCV columns
    # --------------------------------------------------------

    required_columns = [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
    ]

    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:
        raise DataError(
            f"Missing market data columns for "
            f"{symbol}: {missing}"
        )

    # --------------------------------------------------------
    # Keep only required market fields
    # --------------------------------------------------------

    df = df[
        required_columns
    ].copy()

    # --------------------------------------------------------
    # Remove invalid rows
    # --------------------------------------------------------

    df = df.dropna(
        subset=required_columns
    )

    # --------------------------------------------------------
    # Chronological order
    # --------------------------------------------------------

    df = df.sort_index()

    # Remove duplicate timestamps
    df = df[
        ~df.index.duplicated(
            keep="last"
        )
    ]

    # --------------------------------------------------------
    # Final validation
    # --------------------------------------------------------

    if df.empty:
        raise DataError(
            f"No valid OHLCV data available for "
            f"{symbol} / {interval}"
        )

    return df
