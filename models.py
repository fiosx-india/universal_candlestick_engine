from dataclasses import dataclass, field
from typing import Any

@dataclass
class PatternResult:
    name: str
    direction: str
    state: str = "FORMING"
    confidence: float = 0.0
    score: float = 0.0
    timeframe: str = ""
    details: dict[str, Any] = field(default_factory=dict)

@dataclass
class HistoricalOutcome:
    horizon: str
    samples: int
    bullish_probability: float
    bearish_probability: float
    sideways_probability: float
    median_return: float | None = None
    win_rate: float | None = None

@dataclass
class AnalysisResult:
    symbol: str
    timeframe: str
    last_price: float
    trend: str
    volatility: str
    patterns: list[PatternResult] = field(default_factory=list)
    outcomes: list[HistoricalOutcome] = field(default_factory=list)
    projection: dict[str, Any] = field(default_factory=dict)
