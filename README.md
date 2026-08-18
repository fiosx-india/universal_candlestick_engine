# Universal Candlestick Engine

Streamlit-first, reusable candlestick and chart-pattern intelligence engine.

## Baseline v0.1
- OHLCV normalization and resampling
- 1m/5m/15m/30m/45m/1H–8H, daily, weekly and monthly timeframe registry
- Core candlestick patterns
- Structural pattern candidates: W/M, V, H&S, inverse H&S, triangles, wedges, flags, cup/handle, rounding bottom, triple top/bottom
- Trend, volatility and multi-timeframe context
- Historical forward-outcome statistics
- Probability and projection layers
- Plotly candlestick chart
- Streamlit multipage UI
- Basic backtesting/validation utilities

## Run
```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

This project deliberately reports probabilities and pattern states rather than guaranteeing future price direction.
