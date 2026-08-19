# ============================================================
# ANGEL ONE SMARTAPI DATA PROVIDER
# ============================================================
#
# Purpose:
#   Universal Candlestick Engine-க்கு Angel One historical
#   OHLCV market data வழங்குவது.
#
# IMPORTANT:
#   - இந்த module order place செய்யாது.
#   - இது historical market data மட்டும் பெறும்.
#   - Pattern / probability logic இதில் இருக்காது.
#   - Broker-specific logic இந்த file-க்குள் மட்டும் இருக்கும்.
#
# Supported native intervals:
#   1m, 5m, 15m, 30m, 1H, 1D
#
# 45m / 2H / 4H / 8H / 2D / 15D / etc.
# existing service.py aggregation engine மூலம் உருவாக்கப்படும்.
# ============================================================

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

import pandas as pd
import requests
from pyotp import TOTP

from SmartApi import SmartConnect


# ============================================================
# ANGEL ONE INSTRUMENT MASTER
# ============================================================

INSTRUMENT_MASTER_URL = (
    "https://margincalculator.angelbroking.com/"
    "OpenAPI_File/files/OpenAPIScripMaster.json"
)


# ============================================================
# ANGEL ONE INTERVAL MAPPING
# ============================================================

ANGEL_INTERVALS = {
    "1m": "ONE_MINUTE",
    "5m": "FIVE_MINUTE",
    "15m": "FIFTEEN_MINUTE",
    "30m": "THIRTY_MINUTE",
    "1H": "ONE_HOUR",
    "1h": "ONE_HOUR",
    "1D": "ONE_DAY",
    "1d": "ONE_DAY",
}


# ============================================================
# MAXIMUM SAFE REQUEST WINDOW
# ============================================================
#
# Based on Angel One Historical API limits.
#
# 1-minute data can be very large, therefore we deliberately
# use 20-day chunks instead of requesting the full 30 days.
# This also helps stay below large-record responses.
# ============================================================

REQUEST_WINDOWS = {
    "ONE_MINUTE": 20,
    "FIVE_MINUTE": 100,
    "FIFTEEN_MINUTE": 200,
    "THIRTY_MINUTE": 200,
    "ONE_HOUR": 400,
    "ONE_DAY": 2000,
}


# ============================================================
# EXCHANGE NORMALIZATION
# ============================================================

SUPPORTED_EXCHANGES = {
    "NSE",
    "BSE",
    "NFO",
    "BFO",
    "MCX",
    "CDS",
}


def _normalize_exchange(exchange: str) -> str:
    """
    Normalize and validate Angel One exchange segment.
    """

    value = str(exchange).strip().upper()

    if value not in SUPPORTED_EXCHANGES:
        raise ValueError(
            f"Unsupported Angel One exchange: {exchange}"
        )

    return value


# ============================================================
# SYMBOL NORMALIZATION
# ============================================================

def _normalize_symbol(symbol: str) -> str:
    """
    Convert common symbol formats into a searchable
    Angel One symbol name.

    Examples:
        RELIANCE.NS -> RELIANCE
        RELIANCE     -> RELIANCE
        TCS.NS       -> TCS
    """

    value = str(symbol).strip().upper()

    if value.endswith(".NS"):
        value = value[:-3]

    elif value.endswith(".BO"):
        value = value[:-3]

    return value


# ============================================================
# ANGEL ONE DATA CLIENT
# ============================================================

class AngelOneDataClient:
    """
    Historical market-data client for Angel One SmartAPI.

    This class intentionally does NOT expose order placement
    functionality.

    It only provides normalized OHLCV data to the Universal
    Candlestick Engine.
    """

    def __init__(
        self,
        api_key: str,
        client_code: str,
        mpin: str,
        totp_secret: str,
        instrument_master_url: str = INSTRUMENT_MASTER_URL,
    ):

        if not api_key:
            raise ValueError(
                "Angel One API key is missing."
            )

        if not client_code:
            raise ValueError(
                "Angel One client code is missing."
            )

        if not mpin:
            raise ValueError(
                "Angel One MPIN is missing."
            )

        if not totp_secret:
            raise ValueError(
                "Angel One TOTP secret is missing."
            )

        self.api_key = str(api_key).strip()
        self.client_code = str(client_code).strip()
        self.mpin = str(mpin).strip()
        self.totp_secret = str(totp_secret).strip()
        self.instrument_master_url = (
            instrument_master_url
        )

        self.smart_api = None
        self._instrument_master = None
        self._token_cache = {}

    def search_instruments(
        self,
        exchange: str,
        query: str,
        limit: int = 50,
    ):
        """
        Search Angel One instruments using the existing
        authenticated SmartConnect session.
        """

        from data.instrument_registry import search_instruments

        return search_instruments(
            angel_client=self.client,
            exchange=exchange,
            query=query,
            limit=limit,
        )

    def resolve_instrument(
        self,
        exchange: str,
        query: str,
    ):
        """
        Resolve user-facing instrument name into the
        exact Angel One trading symbol and token.
        """

        from data.instrument_registry import resolve_instrument

        return resolve_instrument(
            angel_client=self.client,
            exchange=exchange,
            query=query,
        )


    # ========================================================
    # LOGIN
    # ========================================================

    def login(self):
        """
        Create a fresh Angel One SmartAPI session.
        """

        self.smart_api = SmartConnect(
            api_key=self.api_key
        )

        totp = TOTP(
            self.totp_secret
        ).now()

        session = self.smart_api.generateSession(
            self.client_code,
            self.mpin,
            totp,
        )

        if not session:
            raise RuntimeError(
                "Angel One returned an empty login response."
            )

        if not session.get("status", False):
            message = session.get(
                "message",
                "Unknown Angel One login error.",
            )

            error_code = session.get(
                "errorcode",
                "",
            )

            raise RuntimeError(
                "Angel One login failed: "
                f"{message} "
                f"{error_code}"
            )

        return session

    # ========================================================
    # ENSURE LOGIN
    # ========================================================

    def _ensure_login(self):
        if self.smart_api is None:
            self.login()

    # ========================================================
    # INSTRUMENT MASTER
    # ========================================================

    def _load_instrument_master(self):
        """
        Download Angel One instrument master once and cache it.
        """

        if self._instrument_master is not None:
            return self._instrument_master

        response = requests.get(
            self.instrument_master_url,
            timeout=30,
        )

        response.raise_for_status()

        instruments = response.json()

        if not isinstance(instruments, list):
            raise RuntimeError(
                "Angel One instrument master returned "
                "an unexpected response."
            )

        self._instrument_master = instruments

        return instruments

    # ========================================================
    # SYMBOL TOKEN LOOKUP
    # ========================================================

    def resolve_symbol(
        self,
        symbol: str,
        exchange: str = "NSE",
    ) -> dict:
        """
        Resolve a user-facing symbol to Angel One's
        trading symbol and symbol token.
        """

        exchange = _normalize_exchange(
            exchange
        )

        normalized_symbol = _normalize_symbol(
            symbol
        )

        cache_key = (
            exchange,
            normalized_symbol,
        )

        if cache_key in self._token_cache:
            return self._token_cache[cache_key]

        instruments = self._load_instrument_master()

        # ----------------------------------------------------
        # First preference:
        # Normal equity symbol ending in -EQ.
        # ----------------------------------------------------

        candidates = []

        for item in instruments:

            if item.get("exch_seg") != exchange:
                continue

            item_name = str(
                item.get("name", "")
            ).upper()

            trading_symbol = str(
                item.get("symbol", "")
            ).upper()

            if item_name != normalized_symbol:
                continue

            candidates.append(item)

        # ----------------------------------------------------
        # Prefer regular equity contract.
        # ----------------------------------------------------

        equity_candidates = [
            item
            for item in candidates
            if str(
                item.get("symbol", "")
            ).upper().endswith("-EQ")
        ]

        if equity_candidates:
            candidates = equity_candidates

        if not candidates:
            raise ValueError(
                f"Angel One symbol not found: "
                f"{normalized_symbol} "
                f"on {exchange}"
            )

        selected = candidates[0]

        result = {
            "exchange": exchange,
            "symbol": selected.get(
                "symbol"
            ),
            "name": selected.get(
                "name"
            ),
            "token": str(
                selected.get("token")
            ),
        }

        self._token_cache[cache_key] = result

        return result

    # ========================================================
    # INTERVAL RESOLUTION
    # ========================================================

    def _resolve_interval(
        self,
        interval: str,
    ) -> str:

        key = str(interval).strip()

        if key not in ANGEL_INTERVALS:
            raise ValueError(
                f"Unsupported Angel One interval: "
                f"{interval}"
            )

        return ANGEL_INTERVALS[key]

    # ========================================================
    # REQUEST WINDOW
    # ========================================================

    def _request_window_days(
        self,
        angel_interval: str,
    ) -> int:

        return REQUEST_WINDOWS.get(
            angel_interval,
            20,
        )

    # ========================================================
    # SINGLE HISTORICAL REQUEST
    # ========================================================

    def _get_candle_chunk(
        self,
        exchange: str,
        symbol_token: str,
        interval: str,
        start: datetime,
        end: datetime,
    ) -> list:

        self._ensure_login()

        params = {
            "exchange": exchange,
            "symboltoken": str(
                symbol_token
            ),
            "interval": interval,
            "fromdate": start.strftime(
                "%Y-%m-%d %H:%M"
            ),
            "todate": end.strftime(
                "%Y-%m-%d %H:%M"
            ),
        }

        response = self.smart_api.getCandleData(
            params
        )

        if response is None:
            raise RuntimeError(
                "Angel One returned no response."
            )

        if not response.get(
            "status",
            False,
        ):
            message = response.get(
                "message",
                "Unknown historical data error.",
            )

            error_code = response.get(
                "errorcode",
                "",
            )

            raise RuntimeError(
                "Angel One historical data failed: "
                f"{message} "
                f"{error_code}"
            )

        rows = response.get(
            "data"
        )

        if rows is None:
            return []

        return rows

    # ========================================================
    # NORMALIZE CANDLE RESPONSE
    # ========================================================

    @staticmethod
    def _normalize_candles(
        rows: list,
    ) -> pd.DataFrame:

        if not rows:
            return pd.DataFrame(
                columns=[
                    "Open",
                    "High",
                    "Low",
                    "Close",
                    "Volume",
                ]
            )

        records = []

        for row in rows:

            if not isinstance(
                row,
                (list, tuple),
            ):
                continue

            if len(row) < 6:
                continue

            records.append(
                [
                    row[0],
                    row[1],
                    row[2],
                    row[3],
                    row[4],
                    row[5],
                ]
            )

        if not records:
            return pd.DataFrame(
                columns=[
                    "Open",
                    "High",
                    "Low",
                    "Close",
                    "Volume",
                ]
            )

        data = pd.DataFrame(
            records,
            columns=[
                "Datetime",
                "Open",
                "High",
                "Low",
                "Close",
                "Volume",
            ],
        )

        data["Datetime"] = pd.to_datetime(
            data["Datetime"],
            errors="coerce",
        )

        for column in [
            "Open",
            "High",
            "Low",
            "Close",
            "Volume",
        ]:

            data[column] = pd.to_numeric(
                data[column],
                errors="coerce",
            )

        data.dropna(
            subset=[
                "Datetime",
                "Open",
                "High",
                "Low",
                "Close",
            ],
            inplace=True,
        )

        data.set_index(
            "Datetime",
            inplace=True,
        )

        # ----------------------------------------------------
        # Remove timezone.
        #
        # The rest of our engine works with normal pandas
        # DatetimeIndex values.
        # ----------------------------------------------------

        if getattr(
            data.index,
            "tz",
            None,
        ) is not None:

            data.index = (
                data.index.tz_localize(
                    None
                )
            )

        data = data[
            ~data.index.duplicated(
                keep="last"
            )
        ]

        data.sort_index(
            inplace=True
        )

        return data[
            [
                "Open",
                "High",
                "Low",
                "Close",
                "Volume",
            ]
        ]

    # ========================================================
    # HISTORICAL OHLCV
    # ========================================================

    def get_historical_data(
        self,
        symbol: str,
        interval: str = "1D",
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        exchange: str = "NSE",
    ) -> pd.DataFrame:
        """
        Fetch historical OHLCV data.

        Automatically:
            1. logs in
            2. resolves symbol token
            3. splits large date ranges
            4. downloads each chunk
            5. combines results
            6. removes duplicates
            7. returns standard OHLCV DataFrame
        """

        exchange = _normalize_exchange(
            exchange
        )

        angel_interval = (
            self._resolve_interval(
                interval
            )
        )

        symbol_info = self.resolve_symbol(
            symbol,
            exchange=exchange,
        )

        if end is None:
            end = datetime.now()

        if start is None:
            start = end - timedelta(
                days=365
            )

        if start >= end:
            raise ValueError(
                "Historical data start must be "
                "earlier than end."
            )

        chunk_days = (
            self._request_window_days(
                angel_interval
            )
        )

        all_rows = []

        cursor = start

        while cursor < end:

            chunk_end = min(
                cursor
                + timedelta(
                    days=chunk_days
                ),
                end,
            )

            rows = self._get_candle_chunk(
                exchange=exchange,
                symbol_token=symbol_info[
                    "token"
                ],
                interval=angel_interval,
                start=cursor,
                end=chunk_end,
            )

            if rows:
                all_rows.extend(
                    rows
                )

            # ------------------------------------------------
            # Move forward.
            # ------------------------------------------------

            cursor = chunk_end

        data = self._normalize_candles(
            all_rows
        )

        if data.empty:
            raise ValueError(
                f"No Angel One historical data "
                f"returned for {symbol} "
                f"({interval})."
            )

        # ----------------------------------------------------
        # Final requested range.
        # ----------------------------------------------------

        data = data[
            (data.index >= start)
            & (data.index <= end)
        ]

        if data.empty:
            raise ValueError(
                f"No candles remain after "
                f"date-range filtering for {symbol}."
            )

        return data

    # ========================================================
    # SIMPLE TEST
    # ========================================================

    def test_connection(
        self,
        symbol: str = "RELIANCE",
        exchange: str = "NSE",
        interval: str = "1D",
        days: int = 30,
    ) -> pd.DataFrame:
        """
        Small connection/data test.

        This is intentionally read-only.
        """

        end = datetime.now()

        start = (
            end
            - timedelta(
                days=days
            )
        )

        return self.get_historical_data(
            symbol=symbol,
            interval=interval,
            start=start,
            end=end,
            exchange=exchange,
      )
