"""Candlestick patterns for synthetics."""

import numpy as np
import pandas as pd


class SyntheticCandlestickPatterns:
    """Candlestick patterns specific to synthetics."""

    @staticmethod
    def mechanical_doji(data: pd.DataFrame) -> float:
        """
        Detect mechanical doji patterns in synthetics.
        
        Returns pattern signal 0-100.
        """
        if len(data) < 1:
            return 50.0

        open_price = data['Open'].values[-1]
        close_price = data['Close'].values[-1]
        high = data['High'].values[-1]
        low = data['Low'].values[-1]

        body_size = abs(close_price - open_price)
        total_range = high - low

        if total_range == 0:
            return 50.0

        # Synthetic doji: very small body relative to range
        if body_size < total_range * 0.05:
            return 85.0
        else:
            return 50.0

    @staticmethod
    def synthetic_reversal_candle(data: pd.DataFrame) -> float:
        """
        Detect reversal patterns in synthetics.
        
        Returns reversal signal 0-100.
        """
        if len(data) < 2:
            return 50.0

        current_open = data['Open'].values[-1]
        current_close = data['Close'].values[-1]
        prev_close = data['Close'].values[-2]

        # Candle that reverses from previous direction
        prev_direction = prev_close - data['Open'].values[-2]
        current_direction = current_close - current_open

        if (prev_direction > 0 and current_direction < 0) or \
           (prev_direction < 0 and current_direction > 0):
            return 75.0
        else:
            return 50.0

    @staticmethod
    def synthetic_range_candle(data: pd.DataFrame) -> float:
        """
        Identify range-defining candles.
        
        Returns signal 0-100.
        """
        if len(data) < 1:
            return 50.0

        high = data['High'].values[-1]
        low = data['Low'].values[-1]
        range_val = high - low

        avg_range = np.mean(data['High'].values[-10:] - data['Low'].values[-10:])

        if range_val > avg_range * 2:
            return 80.0
        else:
            return 50.0

    @staticmethod
    def synthetic_breakout_candle(data: pd.DataFrame) -> float:
        """
        Identify breakout candles.
        
        Returns signal 0-100.
        """
        if len(data) < 10:
            return 50.0

        high = data['High'].values[-1]
        prev_high = np.max(data['High'].values[-10:-1])

        low = data['Low'].values[-1]
        prev_low = np.min(data['Low'].values[-10:-1])

        if high > prev_high:
            return 80.0
        elif low < prev_low:
            return 20.0
        else:
            return 50.0
