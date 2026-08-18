from dataclasses import dataclass

@dataclass
class AnalysisRequest:
    symbol: str
    timeframe: str = "1D"
    period: str = "2y"
