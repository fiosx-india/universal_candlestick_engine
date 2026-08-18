from dataclasses import dataclass

DEFAULT_SYMBOL = "RELIANCE.NS"
DEFAULT_TIMEFRAME = "1D"
DEFAULT_LOOKBACK = "2y"
DEFAULT_VOLUME_WINDOW = 20
DEFAULT_ATR_WINDOW = 14

@dataclass(frozen=True)
class EngineConfig:
    volume_window: int = DEFAULT_VOLUME_WINDOW
    atr_window: int = DEFAULT_ATR_WINDOW
    doji_body_ratio: float = 0.10
    wick_body_ratio: float = 2.0
    confirmation_bars: int = 2
    forward_horizons: tuple[str, ...] = ("1H", "4H", "1D", "2D", "3D", "5D", "7D", "15D")
