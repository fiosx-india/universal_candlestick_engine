import numpy as np
import pandas as pd


# ============================================================
# FORWARD OUTCOME HORIZONS
# ============================================================
#
# Each horizon represents the number of candles/bars to look
# forward from the candle where a pattern occurred.
#
# NOTE:
# 1H/2H/3H... are meaningful when the input dataframe itself
# contains hourly candles.
#
# 1D/2D/... are meaningful when the dataframe contains daily
# candles.
#
# 1W/2W/... are meaningful when the dataframe contains weekly
# candles.
#
# 1M/2M/... are meaningful when the dataframe contains monthly
# candles.
# ============================================================

HORIZON_BARS = {
    # Hour horizons
    "1H": 1,
    "2H": 2,
    "3H": 3,
    "4H": 4,
    "5H": 5,
    "6H": 6,
    "7H": 7,
    "8H": 8,

    # Day horizons
    "1D": 1,
    "2D": 2,
    "3D": 3,
    "4D": 4,
    "5D": 5,
    "6D": 6,
    "7D": 7,
    "10D": 10,
    "15D": 15,

    # Week horizons
    "1W": 1,
    "2W": 2,
    "3W": 3,
    "4W": 4,

    # Month horizons
    "1M": 1,
    "2M": 2,
    "3M": 3,
    "4M": 4,
    "5M": 5,
    "6M": 6,
    "7M": 7,
    "8M": 8,
    "9M": 9,
    "10M": 10,
    "11M": 11,
    "12M": 12,
}


# ============================================================
# DEFAULT HORIZONS
# ============================================================

DEFAULT_HORIZONS = list(HORIZON_BARS.keys())


# ============================================================
# SINGLE HORIZON OUTCOME
# ============================================================

def forward_outcomes(
    df,
    occurrence_indices,
    horizon,
):
    """
    Calculate forward price outcomes after a pattern occurrence.

    Parameters
    ----------
    df : pandas.DataFrame
        OHLC dataframe containing a Close column.

    occurrence_indices : iterable
        Index values where the pattern occurred.

    horizon : str
        Example:
        1H, 2H, 4H,
        1D, 2D, 5D,
        1W, 2W,
        1M, 3M, 12M.

    Returns
    -------
    dict or None
        Historical probability/outcome statistics.
    """

    bars = HORIZON_BARS.get(horizon)

    if bars is None:
        return None

    if df is None or df.empty:
        return None

    if "Close" not in df.columns:
        return None

    closes = pd.to_numeric(
        df["Close"],
        errors="coerce",
    )

    if closes.empty:
        return None

    returns = []

    for idx in occurrence_indices:

        try:
            positions = df.index.get_indexer([idx])

            if len(positions) == 0:
                continue

            pos = positions[0]

            if pos < 0:
                continue

        except Exception:
            continue

        # Not enough future data
        if pos + bars >= len(df):
            continue

        start = closes.iloc[pos]
        end = closes.iloc[pos + bars]

        if pd.isna(start) or pd.isna(end):
            continue

        start = float(start)
        end = float(end)

        if start <= 0:
            continue

        future_return = (
            end / start
        ) - 1.0

        returns.append(
            future_return
        )

    if not returns:
        return None

    arr = np.asarray(
        returns,
        dtype=float,
    )

    # --------------------------------------------------------
    # Classification thresholds
    # --------------------------------------------------------
    #
    # > +0.20%  = bullish
    # < -0.20%  = bearish
    # otherwise  = sideways
    #
    # These are classification thresholds, NOT guarantees.
    # --------------------------------------------------------

    bullish_probability = float(
        (arr > 0.002).mean()
    )

    bearish_probability = float(
        (arr < -0.002).mean()
    )

    sideways_probability = max(
        0.0,
        1.0
        - bullish_probability
        - bearish_probability,
    )

    median_return = float(
        np.median(arr)
    )

    mean_return = float(
        np.mean(arr)
    )

    win_rate = float(
        (arr > 0).mean()
    )

    loss_rate = float(
        (arr < 0).mean()
    )

    return {
        "horizon": horizon,
        "samples": int(len(arr)),

        "bullish_probability":
            bullish_probability,

        "bearish_probability":
            bearish_probability,

        "sideways_probability":
            sideways_probability,

        "median_return":
            median_return,

        "mean_return":
            mean_return,

        "win_rate":
            win_rate,

        "loss_rate":
            loss_rate,
    }


# ============================================================
# ALL HORIZONS
# ============================================================

def forward_outcomes_all(
    df,
    occurrence_indices,
    horizons=None,
):
    """
    Calculate forward outcomes for every requested horizon.

    This is the function consumed by api/service.py.
    """

    if horizons is None:
        horizons = DEFAULT_HORIZONS

    results = {}

    for horizon in horizons:

        if horizon not in HORIZON_BARS:
            continue

        outcome = forward_outcomes(
            df=df,
            occurrence_indices=occurrence_indices,
            horizon=horizon,
        )

        if outcome is not None:
            results[horizon] = outcome

    return results


# ============================================================
# CURRENT / MOST RECENT OUTCOME
# ============================================================

def calculate_single_forward_return(
    df,
    occurrence_index,
    horizon,
):
    """
    Calculate the actual forward return for one
    specific pattern occurrence and one horizon.
    """

    result = forward_outcomes(
        df=df,
        occurrence_indices=[
            occurrence_index
        ],
        horizon=horizon,
    )

    if not result:
        return None

    return result.get(
        "median_return"
    )


# ============================================================
# OUTCOME DIRECTION
# ============================================================

def classify_return(
    return_value,
    bullish_threshold=0.002,
    bearish_threshold=-0.002,
):
    """
    Convert a return into a simple market direction.
    """

    if return_value is None:
        return "UNKNOWN"

    value = float(
        return_value
    )

    if value > bullish_threshold:
        return "BULLISH"

    if value < bearish_threshold:
        return "BEARISH"

    return "SIDEWAYS"


# ============================================================
# OUTCOME SUMMARY
# ============================================================

def summarize_outcome(
    outcome,
):
    """
    Add a human-readable directional classification
    to an outcome dictionary.
    """

    if not outcome:
        return None

    result = dict(outcome)

    result["direction"] = classify_return(
        result.get(
            "median_return"
        )
    )

    return result
