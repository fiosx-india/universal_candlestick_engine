"""
Universal Candlestick Engine
Angel One Instrument Registry

Purpose:
    Centralize Angel One instrument discovery and resolution.

Important:
    - Angel One remains the source of truth.
    - No hard-coded commodity tokens.
    - MCX historical-analysis search returns FUT contracts only.
    - MCX COM / CE / PE entries are excluded from the historical
      market-analysis selector.
    - Active/nearest-expiry MCX futures are ranked first.
"""

from __future__ import annotations

from datetime import datetime, date
from typing import Any


# ------------------------------------------------------------
# DISPLAY / SEARCH EXCHANGES
# ------------------------------------------------------------

SUPPORTED_EXCHANGES = [
    "NSE",
    "BSE",
    "MCX",
    "NFO",
    "BFO",
    "CDS",
]


# ------------------------------------------------------------
# COMMON USER ALIASES
# ------------------------------------------------------------

ALIASES = {
    "NIFTY": "NIFTY",
    "NIFTY 50": "NIFTY",
    "NIFTY50": "NIFTY",

    "BANKNIFTY": "BANKNIFTY",
    "BANK NIFTY": "BANKNIFTY",

    "SENSEX": "SENSEX",
    "BANKEX": "BANKEX",

    "GOLD": "GOLD",
    "SILVER": "SILVER",
    "CRUDEOIL": "CRUDEOIL",
    "CRUDE OIL": "CRUDEOIL",
    "NATURALGAS": "NATURALGAS",
    "NATURAL GAS": "NATURALGAS",
}


def normalize_query(value: str) -> str:
    """Normalize user search text."""

    value = str(value or "").strip().upper()

    for suffix in (".NS", ".BO"):
        if value.endswith(suffix):
            value = value[:-len(suffix)]

    value = " ".join(value.split())

    return ALIASES.get(value, value)


def _safe_row(row: Any) -> dict[str, Any] | None:
    """Return a normalized instrument row."""

    if not isinstance(row, dict):
        return None

    trading_symbol = row.get("tradingsymbol")
    token = row.get("symboltoken")

    if not trading_symbol or not token:
        return None

    return {
        "exchange": str(row.get("exchange") or "").upper(),
        "tradingsymbol": str(trading_symbol),
        "symboltoken": str(token),
        "name": str(
            row.get("name")
            or row.get("symbol")
            or trading_symbol
        ),
        "lotsize": row.get("lotsize"),
        "instrumenttype": row.get("instrumenttype"),
        "expiry": row.get("expiry"),
        "strike": row.get("strike"),
    }


# ------------------------------------------------------------
# MCX HISTORICAL-ANALYSIS ELIGIBILITY
# ------------------------------------------------------------

def _is_mcx_historical_candidate(
    row: dict[str, Any],
) -> bool:
    """
    Keep only MCX futures suitable for historical OHLC analysis.

    Angel One's MCX search can return:
        - COM/reference entries
        - FUT contracts
        - CE options
        - PE options

    This engine analyses the underlying futures price series, so
    only FUT contracts are allowed into the historical selector.
    """

    symbol = str(
        row.get("tradingsymbol") or ""
    ).strip().upper()

    instrument_type = str(
        row.get("instrumenttype") or ""
    ).strip().upper()

    # Explicitly reject option contracts.
    if symbol.endswith("CE") or symbol.endswith("PE"):
        return False

    # Explicitly reject commodity/reference entries.
    if symbol.endswith("COM"):
        return False

    # MCX futures are normally identified by FUT in the trading
    # symbol and/or instrument type. Prefer the symbol because it
    # is the exact value sent to the historical API.
    if "FUT" in symbol:
        return True

    if instrument_type in {
        "FUTCOM",
        "FUTIDX",
        "FUTSTK",
    }:
        return True

    return False


# ------------------------------------------------------------
# EXPIRY PARSING / RANKING
# ------------------------------------------------------------

def _parse_expiry(value: Any) -> date | None:
    """Parse common Angel One expiry representations."""

    if value is None:
        return None

    text = str(value).strip().upper()

    if not text:
        return None

    formats = (
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%d%b%Y",
        "%d%b%y",
        "%d-%b-%Y",
        "%d-%b-%y",
        "%Y%m%d",
    )

    for fmt in formats:
        try:
            return datetime.strptime(
                text,
                fmt,
            ).date()
        except ValueError:
            continue

    # Some feeds may provide ISO timestamps.
    try:
        return datetime.fromisoformat(
            text.replace("Z", "+00:00")
        ).date()
    except ValueError:
        return None


def _expiry_rank(
    row: dict[str, Any],
) -> tuple[int, int]:
    """
    Rank MCX futures by expiry.

    Active future:
        expiry >= today

    Nearest future:
        smallest positive number of days to expiry

    Unknown expiry:
        placed after known expiries.
    """

    expiry = _parse_expiry(
        row.get("expiry")
    )

    if expiry is None:
        return (1, 10**9)

    days = (
        expiry - date.today()
    ).days

    if days < 0:
        return (1, days)

    return (0, days)


# ------------------------------------------------------------
# SEARCH RANKING
# ------------------------------------------------------------

def rank_instrument(
    row: dict[str, Any],
    query: str,
    exchange: str,
) -> tuple:
    """
    Rank Angel One search results.

    For NSE/BSE:
        exact symbol > -EQ > exact name > prefix > shorter symbol

    For MCX:
        exact match > active FUT > nearest expiry > exact name/prefix
        > shorter symbol
    """

    symbol = row["tradingsymbol"].upper()
    name = row["name"].upper()
    query = query.upper()
    exchange = exchange.upper()

    exact = int(symbol == query)
    equity = int(symbol == f"{query}-EQ")
    exact_name = int(name == query)
    prefix = int(symbol.startswith(query))

    if exchange == "MCX":
        expiry_state, expiry_days = _expiry_rank(row)

        # Futures must already have passed the eligibility filter.
        # Active/nearest-expiry contracts are preferred.
        return (
            exact,
            1,
            -expiry_state,
            -expiry_days,
            exact_name,
            prefix,
            -len(symbol),
            symbol,
        )

    return (
        exact,
        equity,
        exact_name,
        prefix,
        -len(symbol),
        symbol,
    )


# ------------------------------------------------------------
# SEARCH
# ------------------------------------------------------------

def search_instruments(
    angel_client: Any,
    exchange: str,
    query: str,
    limit: int = 50,
) -> list[dict[str, Any]]:
    """
    Search Angel One instruments.

    For MCX historical analysis, only futures contracts are returned.
    For all other exchanges, existing search behaviour is preserved.
    """

    exchange = str(
        exchange or ""
    ).strip().upper()

    query = normalize_query(query)

    if exchange not in SUPPORTED_EXCHANGES:
        raise ValueError(
            f"Unsupported Angel One exchange: {exchange}"
        )

    if not query:
        return []

    response = angel_client.searchScrip(
        exchange,
        query,
    )

    if not isinstance(response, dict):
        return []

    if not response.get("status"):
        return []

    rows = response.get("data") or []

    results: list[dict[str, Any]] = []

    for raw in rows:
        row = _safe_row(raw)

        if row is None:
            continue

        if (
            row["exchange"]
            and row["exchange"] != exchange
        ):
            continue

        # MCX historical-analysis filter.
        if (
            exchange == "MCX"
            and not _is_mcx_historical_candidate(row)
        ):
            continue

        results.append(row)

    results.sort(
        key=lambda row: rank_instrument(
            row,
            query,
            exchange,
        ),
        reverse=True,
    )

    return results[:max(1, int(limit))]


# ------------------------------------------------------------
# RESOLUTION
# ------------------------------------------------------------

def resolve_instrument(
    angel_client: Any,
    exchange: str,
    query: str,
) -> dict[str, Any]:
    """
    Resolve one user instrument into the exact Angel One
    trading symbol and symbol token.

    MCX resolution never falls back to COM / CE / PE entries.
    """

    exchange = str(
        exchange or ""
    ).strip().upper()

    requested = normalize_query(query)

    results = search_instruments(
        angel_client=angel_client,
        exchange=exchange,
        query=requested,
        limit=50,
    )

    if not results:
        if exchange == "MCX":
            raise ValueError(
                f"No usable MCX FUT contract found for "
                f"{requested}."
            )

        raise ValueError(
            f"Angel One instrument not found: "
            f"{requested} on {exchange}"
        )

    # Exact symbol match first.
    for row in results:
        if (
            row["tradingsymbol"].upper()
            == requested
        ):
            return row

    # Regular equity match next.
    for row in results:
        if (
            row["tradingsymbol"].upper()
            == f"{requested}-EQ"
        ):
            return row

    # MCX: search results are already filtered and expiry-ranked.
    return results[0]
