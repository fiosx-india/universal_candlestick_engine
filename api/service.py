import numpy as np
import pandas as pd


# ============================================================
# UNIVERSAL FORWARD OUTCOME HORIZONS
# ============================================================
#
# N = number of bars forward on the CURRENT analysis timeframe.
#
# Example:
#   1H chart:
#       1H = 1 bar
#       2H = 2 bars
#       ...
#       8H = 8 bars
#
#   1D chart:
#       1D = 1 bar
#       2D = 2 bars
#       ...
#       15D = 15 bars
#
#   1W chart:
#       1W = 1 bar
#       2W = 2 bars
#       ...
#
#   1M chart:
#       1M = 1 bar
#       ...
#       12M = 12 bars
#
# IMPORTANT:
# These are historical probabilities.
# They are NOT guaranteed future predictions.
# ============================================================

HORIZON_BARS = {

    # --------------------------------------------------------
    # INTRADAY / HOURLY
    # --------------------------------------------------------
    "1H": 1,
    "2H": 2,
    "3H": 3,
    "4H": 4,
    "5H": 5,
    "6H": 6,
    "7H": 7,
    "8H": 8,

    # --------------------------------------------------------
    # DAILY
    # --------------------------------------------------------
    "1D": 1,
    "2D": 2,
    "3D": 3,
    "4D": 4,
    "5D": 5,
    "6D": 6,
    "7D": 7,
    "10D": 10,
    "15D": 15,

    # --------------------------------------------------------
    # WEEKLY
    # --------------------------------------------------------
    "1W": 1,
    "2W": 2,
    "3W": 3,
    "4W": 4,

    # --------------------------------------------------------
    # MONTHLY
    # --------------------------------------------------------
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
# INTERNAL INDEX POSITION RESOLVER
# ============================================================

def _position(index, idx):
    """
    Convert a dataframe index label into an integer row position.

    This keeps the outcome engine safe when working with
    DatetimeIndex or other pandas index types.
    """

    try:
        loc = index.get_loc(idx)

    except KeyError:
        return None

    # Normal unique index
    if isinstance(loc, (int, np.integer)):
        return int(loc)

    # Duplicate index protection
    if isinstance(loc, slice):
        return int(loc.start)

    if isinstance(loc, np.ndarray) and loc.size:
        positions = np.flatnonzero(loc)

        if positions.size:
            return int(positions[0])

    return None


# ============================================================
# SINGLE HORIZON OUTCOME CALCULATOR
# ============================================================

def forward_outcomes(
    df: pd.DataFrame,
    occurrence_indices,
    horizon: str,
    bullish_threshold: float = 0.002,
    bearish_threshold: float = -0.002,
):
    """
    Calculate historical price outcomes after a detected pattern.

    Parameters
    ----------
    df:
        OHLC dataframe containing at least a Close column.

    occurrence_indices:
        Index values where the historical pattern occurred.

    horizon:
        Example:
            1H, 2H, 4H, 8H
            1D, 2D, 5D, 15D
            1W, 2W
            1M, 3M, 12M

    bullish_threshold:
        Minimum return considered meaningfully bullish.
        Default = +0.20%.

    bearish_threshold:
        Maximum return considered meaningfully bearish.
        Default = -0.20%.

    Returns
    -------
    dict or None
    """

    # --------------------------------------------------------
    # Validate horizon
    # --------------------------------------------------------

    if horizon not in HORIZON_BARS:
        return None

    if df is None or df.empty:
        return None

    if "Close" not in df.columns:
        return None

    bars_forward = HORIZON_BARS[horizon]

    if bars_forward < 1:
        return None

    # --------------------------------------------------------
    # Clean close series
    # --------------------------------------------------------

    close = pd.to_numeric(
        df["Close"],
        errors="coerce",
    )

    returns = []

    # --------------------------------------------------------
    # Evaluate every historical occurrence
    # --------------------------------------------------------

    for occurrence_index in occurrence_indices:

        position = _position(
            df.index,
            occurrence_index,
        )

        if position is None:
            continue

        future_position = position + bars_forward

        # Not enough future data
        if future_position >= len(df):
            continue

        start_price = close.iloc[position]
        future_price = close.iloc[future_position]

        if pd.isna(start_price):
            continue

        if pd.isna(future_price):
            continue

        if float(start_price) <= 0:
            continue

        # Percentage return
        future_return = (
            float(future_price) / float(start_price)
        ) - 1.0

        returns.append(future_return)

    # --------------------------------------------------------
    # No usable historical samples
    # --------------------------------------------------------

    if not returns:
        return None

    values = np.asarray(
        returns,
        dtype=float,
    )

    # --------------------------------------------------------
    # Classification
    # --------------------------------------------------------

    bullish_probability = float(
        (values >= bullish_threshold).mean()
    )

    bearish_probability = float(
        (values <= bearish_threshold).mean()
    )

    sideways_probability = max(
        0.0,
        1.0
        - bullish_probability
        - bearish_probability,
    )

    # --------------------------------------------------------
    # Additional statistics
    # --------------------------------------------------------

    positive_return_rate = float(
        (values > 0).mean()
    )

    negative_return_rate = float(
        (values < 0).mean()
    )

    win_rate = positive_return_rate

    mean_return = float(
        np.mean(values)
    )

    median_return = float(
        np.median(values)
    )

    # --------------------------------------------------------
    # Final result
    # --------------------------------------------------------

    return {

        "horizon": horizon,

        "bars_forward": bars_forward,

        "samples": int(
            len(values)
        ),

        "bullish_probability": bullish_probability,

        "bearish_probability": bearish_probability,

        "sideways_probability": sideways_probability,

        "mean_return": mean_return,

        "median_return": median_return,

        "win_rate": win_rate,

        "positive_return_rate": positive_return_rate,

        "negative_return_rate": negative_return_rate,
    }


# ============================================================
# ALL HORIZONS CALCULATOR
# ============================================================

def forward_outcomes_all(
    df: pd.DataFrame,
    occurrence_indices,
    horizons=None,
):
    """
    Calculate historical outcomes for multiple horizons.

    If horizons is None, every supported horizon is calculated.
    """

    if horizons is None:

        selected_horizons = list(
            HORIZON_BARS.keys()
        )

    else:

        selected_horizons = list(
            horizons
        )

    results = {}

    for horizon in selected_horizons:

        if horizon not in HORIZON_BARS:
            continue

        results[horizon] = forward_outcomes(
            df=df,
            occurrence_indices=occurrence_indices,
            horizon=horizon,
        )

    return results
