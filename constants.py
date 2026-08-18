DIRECTIONS = ("BULLISH", "BEARISH", "SIDEWAYS")
STATES = ("FORMING", "CONFIRMED", "FAILED", "NEUTRAL")

TIMEFRAMES = [
    "1m","5m","15m","30m","45m",
    "1H","2H","3H","4H","5H","6H","7H","8H",
    "1D","2D","3D","4D","5D","6D","7D","10D","15D",
    "1W","2W","3W","4W",
    "1M","2M","3M","4M","5M","6M","7M","8M","9M","10M","11M","12M",
]

PATTERN_GROUPS = {
    "candlestick": [
        "Doji","Hammer","Shooting Star","Bullish Engulfing","Bearish Engulfing",
        "Bullish Marubozu","Bearish Marubozu","Inside Bar",
        "Morning Star","Evening Star","Three Line Strike"
    ],
    "structure": [
        "W Pattern","M Pattern","V Reversal","Head & Shoulders",
        "Inverse Head & Shoulders","Cup & Handle","Rounding Bottom",
        "Triple Top","Triple Bottom","Rising Wedge","Falling Wedge",
        "Ascending Triangle","Descending Triangle","Symmetrical Triangle",
        "Bullish Flag","Bearish Flag","Rectangle","Broadening Formation"
    ]
}
