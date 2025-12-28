# Strelitzia Trader - MetaTrader 5 Analysis Engine

Production-grade Python application for real-time market analysis directly integrated with MetaTrader 5 terminal via Wine on Debian Linux.

## System Architecture

- **MT5 Integration**: Direct socket connection to running MT5 terminal (Wine-based)
- **Market Data**: Live OHLCV candles from MT5 without external APIs
- **Analysis Engine**: 561+ analysis methods (indicators + multi-candle + patterns)
  - Forex: 192 methods (41 indicators + 1 multi-candle + 50 candlestick + 100 chart)
  - Synthetics: 188 methods (37 indicators + 1 multi-candle + 50 candlestick + 100 chart)
  - General: 181 methods (30 indicators + 1 multi-candle + 50 candlestick + 100 chart)
- **Pattern Detection**: 150+ technical patterns (50 candlestick + 100 chart patterns)
- **Symbol Discovery**: Dynamic categorization of available symbols
- **Modular Design**: Extensible analysis framework

## Requirements

- Python 3.10 or newer
- MetaTrader 5 terminal running via Wine on Debian Linux
- User logged into any MT5-supported broker account
- 4GB+ RAM recommended

## Installation

```bash
cd trader
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

The application will:
1. Connect to running MT5 terminal
2. Display account details and broker information
3. Discover available symbols and auto-categorize them
4. Allow symbol, category, and timeframe selection
5. Begin real-time analysis

## Project Structure

```
trader/
├── main.py                 # Entry point
├── requirements.txt        # Dependencies
├── core/                   # Core application logic
│   ├── app.py             # Main application class
│   ├── lifecycle.py       # Lifecycle management
│   └── logger.py          # Logging system
├── mt5/                    # MT5 integration
│   ├── connector.py       # MT5 connection handler
│   ├── account.py         # Account information
│   ├── symbols.py         # Symbol discovery and management
│   └── market_data.py     # Market data retrieval
├── analysis/              # Analysis modules
│   ├── base.py            # Base analysis class
│   ├── forex/             # Forex analysis (192 methods)
│   ├── synthetics/        # Synthetic indices analysis (188 methods)
│   ├── general/           # General assets analysis (181 methods)
│   └── shared/            # Shared utilities and indicators
│       ├── multi_candle_price_action.py        # Multi-candle behavioral analysis
│       ├── candlestick_patterns_advanced.py    # 50+ candlestick pattern detection
│       └── chart_patterns_advanced.py          # 100+ chart pattern detection
├── ui/                    # User interface
│   └── cli.py             # CLI interface
└── config/                # Configuration
    └── settings.py        # Application settings
```

## Analysis Capabilities

### Forex (192 methods)
- **Indicator Analysis**: 41 technical indicators (trend, momentum, volatility, volume, support/resistance)
- **Multi-Candle Price Action**: 1 behavioral analysis method (HH/HL, LH/LL, BOS, CHOCH)
- **Candlestick Patterns**: 50 single and multi-candle patterns (Doji, Hammer, Engulfing, Harami, Morning Star, Evening Star, Three White Soldiers, Three Black Crows, Kicker, Mat Hold, etc.)
- **Chart Patterns**: 100 technical chart patterns (Double Top/Bottom, Head & Shoulders, Triangles, Flags, Pennants, Wedges, Cup & Handle, Rounding, etc.)

### Synthetic Indices (188 methods)
- **Indicator Analysis**: 37 technical indicators (volatility dynamics, boom/crash, jump behavior, range analysis)
- **Multi-Candle Price Action**: 1 behavioral analysis method
- **Candlestick Patterns**: 50 pattern detection methods
- **Chart Patterns**: 100 pattern detection methods

### Indices, Commodities, Crypto (181 methods)
- **Indicator Analysis**: 30 asset-class-specific indicators with confluence scoring
- **Multi-Candle Price Action**: 1 behavioral analysis method
- **Candlestick Patterns**: 50 pattern detection methods
- **Chart Patterns**: 100 pattern detection methods

## Notes

- No credentials management (uses logged-in MT5 account)
- Analysis-only system (no trade execution)
- Direct MT5 integration without external APIs
- Comprehensive error handling and logging
