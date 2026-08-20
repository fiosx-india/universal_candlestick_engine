from constants import TIMEFRAMES


# Canonical native/derived identifiers used across the project.
# Minute identifiers intentionally use lowercase "m"; monthly
# identifiers use uppercase "M". This prevents 1m from becoming 1M.
NATIVE_INTERVALS = {
    "1m",
    "5m",
    "15m",
    "30m",
    "1H",
    "1D",
    "1W",
    "1M",
}


def normalize_timeframe(tf: str) -> str:
    """
    Normalize timeframe text without collapsing minute and month
    semantics.

    Examples:
        1m  -> 1m
        45m -> 45m
        1h  -> 1H
        1d  -> 1D
        1w  -> 1W
        1mo -> 1M
        60M -> 1H
    """
    raw = str(tf or "").strip().replace(" ", "")

    if not raw:
        raise ValueError("Timeframe cannot be empty.")

    # Minute aliases are detected before upper-casing.
    import re

    minute = re.fullmatch(
        r"(\d+)(m|min|mins|minute|minutes)",
        raw,
    )
    if minute is None:
        minute = re.fullmatch(
            r"(\d+)(min|mins|minute|minutes)",
            raw,
            re.IGNORECASE,
        )
    if minute:
        candidate = f"{int(minute.group(1))}m"
        if candidate in TIMEFRAMES:
            return candidate

    upper = raw.upper()

    if upper in {"60M", "60MIN", "1HR", "1HOUR"}:
        return "1H"

    if upper in {"1MO", "1MONTH"}:
        return "1M"

    if upper in TIMEFRAMES:
        return upper

    raise ValueError(f"Unsupported timeframe: {tf}")


def is_supported(tf: str) -> bool:
    try:
        return normalize_timeframe(tf) in TIMEFRAMES
    except ValueError:
        return False
