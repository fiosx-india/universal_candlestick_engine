"""
Universal Candlestick Engine
Angel One Instrument Registry

Purpose:
    Centralize Angel One instrument discovery and resolution.

Important:
    - No Yahoo symbols.
    - No hard-coded stock list.
    - No hard-coded commodity token list.
    - Angel One remains the source of truth.
"""

from __future__ import annotations

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
# These are only names/aliases.
# Tokens are NEVER hard-coded here.
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

    # Remove Yahoo-style suffixes if user accidentally enters them.
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


def rank_instrument(
    row: dict[str, Any],
    query: str,
    exchange: str,
) -> tuple[int, int, int, str]:
    """
    Rank Angel One search results.

    Higher quality instruments come first.

    Priority:
        1. Exact trading symbol
        2. Equity -EQ
        3. Exact name
        4. Prefix match
        5. Contains match
    """

    symbol = row["tradingsymbol"].upper()
    name = row["name"].upper()
    query = query.upper()

    exact = 1 if symbol == query else 0
    equity = 1 if symbol == f"{query}-EQ" else 0
    exact_name = 1 if name == query else 0
    prefix = 1 if symbol.startswith(query) else 0

    # Smaller string length wins when otherwise similar.
    return (
        exact,
        equity,
        exact_name,
        prefix,
        -len(symbol),
    )


def search_instruments(
    angel_client: Any,
    exchange: str,
    query: str,
    limit: int = 50,
) -> list[dict[str, Any]]:
    """
    Search Angel One instruments.

    `angel_client` must be the authenticated SmartConnect
    client already owned by AngelOneDataClient.

    No second login is created here.
    """

    exchange = str(exchange or "").strip().upper()
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

        if row["exchange"] and row["exchange"] != exchange:
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


def resolve_instrument(
    angel_client: Any,
    exchange: str,
    query: str,
) -> dict[str, Any]:
    """
    Resolve one user instrument into the exact Angel One
    trading symbol and symbol token.
    """

    results = search_instruments(
        angel_client=angel_client,
        exchange=exchange,
        query=query,
        limit=50,
    )

    if not results:
        raise ValueError(
            f"Angel One instrument not found: "
            f"{normalize_query(query)} on {exchange}"
        )

    requested = normalize_query(query)

    # Exact match first.
    for row in results:
        if row["tradingsymbol"].upper() == requested:
            return row

    # Equity match next.
    for row in results:
        if row["tradingsymbol"].upper() == f"{requested}-EQ":
            return row

    # Otherwise use the highest-ranked result.
    return results[0]
