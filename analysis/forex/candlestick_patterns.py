"""Candlestick pattern analysis for Forex."""

import numpy as np
import pandas as pd


class CandlestickPatternAnalysis:
    """Identifies candlestick patterns."""

    @staticmethod
    def doji_pattern(data: pd.DataFrame) -> float:
        """
        Identify Doji pattern (open ≈ close).
        
        Returns Doji signal 0-100.
        """
        if len(data) < 1:
            return 50.0

        open_price = data['Open'].values[-1]
        close_price = data['Close'].values[-1]
        high = data['High'].values[-1]
        low = data['Low'].values[-1]

        body = abs(close_price - open_price)
        total_range = high - low

        if total_range == 0:
            return 50.0

        # Doji has small body and long wicks
        if body < total_range * 0.1:
            return 80.0
        else:
            return 50.0

    @staticmethod
    def hammer_pattern(data: pd.DataFrame) -> float:
        """
        Identify Hammer pattern (bullish reversal).
        
        Returns Hammer signal 0-100.
        """
        if len(data) < 2:
            return 50.0

        open_price = data['Open'].values[-1]
        close_price = data['Close'].values[-1]
        high = data['High'].values[-1]
        low = data['Low'].values[-1]
        prev_close = data['Close'].values[-2]

        body = close_price - open_price
        lower_wick = open_price - low if open_price < close_price else close_price - low
        upper_wick = high - max(open_price, close_price)

        # Hammer: small body, long lower wick, small upper wick
        if lower_wick > body * 2 and upper_wick < body and close_price > open_price:
            return 75.0
        else:
            return 50.0

    @staticmethod
    def inverted_hammer_pattern(data: pd.DataFrame) -> float:
        """
        Identify Inverted Hammer pattern (bearish reversal).
        
        Returns Inverted Hammer signal 0-100.
        """
        if len(data) < 2:
            return 50.0

        open_price = data['Open'].values[-1]
        close_price = data['Close'].values[-1]
        high = data['High'].values[-1]
        low = data['Low'].values[-1]

        body = abs(close_price - open_price)
        upper_wick = high - max(open_price, close_price)
        lower_wick = min(open_price, close_price) - low

        # Inverted hammer: small body, long upper wick, small lower wick
        if upper_wick > body * 2 and lower_wick < body:
            return 25.0
        else:
            return 50.0

    @staticmethod
    def engulfing_pattern(data: pd.DataFrame) -> float:
        """
        Identify Engulfing pattern (reversal).
        
        Returns Engulfing signal 0-100.
        """
        if len(data) < 2:
            return 50.0

        # Current candle
        current_open = data['Open'].values[-1]
        current_close = data['Close'].values[-1]
        current_high = data['High'].values[-1]
        current_low = data['Low'].values[-1]

        # Previous candle
        prev_open = data['Open'].values[-2]
        prev_close = data['Close'].values[-2]
        prev_high = data['High'].values[-2]
        prev_low = data['Low'].values[-2]

        prev_high_low = [prev_open, prev_close]
        current_body = [min(current_open, current_close), max(current_open, current_close)]

        # Bullish engulfing
        if current_open < min(prev_high_low) and current_close > max(prev_high_low):
            return 80.0

        # Bearish engulfing
        if current_open > max(prev_high_low) and current_close < min(prev_high_low):
            return 20.0

        return 50.0

    @staticmethod
    def morning_star_pattern(data: pd.DataFrame) -> float:
        """
        Identify Morning Star pattern (bullish reversal).
        
        Returns Morning Star signal 0-100.
        """
        if len(data) < 3:
            return 50.0

        c1_open = data['Open'].values[-3]
        c1_close = data['Close'].values[-3]
        c2_open = data['Open'].values[-2]
        c2_close = data['Close'].values[-2]
        c3_open = data['Open'].values[-1]
        c3_close = data['Close'].values[-1]

        # Bearish candle, small candle (doji-like), bullish candle
        if (c1_open > c1_close and  # First bearish
            abs(c2_open - c2_close) < abs(c1_open - c1_close) * 0.5 and  # Small middle
            c3_close > c3_open and  # Third bullish
            c3_close > (c1_open + c1_close) / 2):  # Closes above midpoint
            return 80.0
        else:
            return 50.0

    @staticmethod
    def evening_star_pattern(data: pd.DataFrame) -> float:
        """
        Identify Evening Star pattern (bearish reversal).
        
        Returns Evening Star signal 0-100.
        """
        if len(data) < 3:
            return 50.0

        c1_open = data['Open'].values[-3]
        c1_close = data['Close'].values[-3]
        c2_open = data['Open'].values[-2]
        c2_close = data['Close'].values[-2]
        c3_open = data['Open'].values[-1]
        c3_close = data['Close'].values[-1]

        # Bullish candle, small candle, bearish candle
        if (c1_open < c1_close and  # First bullish
            abs(c2_open - c2_close) < abs(c1_open - c1_close) * 0.5 and  # Small middle
            c3_open > c3_close and  # Third bearish
            c3_close < (c1_open + c1_close) / 2):  # Closes below midpoint
            return 20.0
        else:
            return 50.0

    @staticmethod
    def pin_bar_pattern(data: pd.DataFrame) -> float:
        """
        Identify Pin Bar pattern (reversal wick).
        
        Returns Pin Bar signal 0-100.
        """
        if len(data) < 1:
            return 50.0

        open_price = data['Open'].values[-1]
        close_price = data['Close'].values[-1]
        high = data['High'].values[-1]
        low = data['Low'].values[-1]

        body = abs(close_price - open_price)
        total_range = high - low

        if total_range == 0:
            return 50.0

        # Pin bar: long wick, small body
        if body < total_range * 0.3 and (high - low) > body * 2:
            # Bullish pin bar
            if low == np.min(data['Low'].values[-3:]):
                return 75.0
            # Bearish pin bar
            elif high == np.max(data['High'].values[-3:]):
                return 25.0

        return 50.0

    @staticmethod
    def inside_bar_pattern(data: pd.DataFrame) -> float:
        """
        Identify Inside Bar pattern (consolidation).
        
        Returns Inside Bar signal 0-100.
        """
        if len(data) < 2:
            return 50.0

        current_high = data['High'].values[-1]
        current_low = data['Low'].values[-1]
        prev_high = data['High'].values[-2]
        prev_low = data['Low'].values[-2]

        # Inside bar: within previous bar's range
        if current_high < prev_high and current_low > prev_low:
            return 70.0
        else:
            return 50.0

    @staticmethod
    def outside_bar_pattern(data: pd.DataFrame) -> float:
        """
        Identify Outside Bar pattern (expansion).
        
        Returns Outside Bar signal 0-100.
        """
        if len(data) < 2:
            return 50.0

        current_high = data['High'].values[-1]
        current_low = data['Low'].values[-1]
        prev_high = data['High'].values[-2]
        prev_low = data['Low'].values[-2]

        # Outside bar: exceeds previous bar's range
        if current_high > prev_high and current_low < prev_low:
            return 75.0
        else:
            return 50.0

    @staticmethod
    def marubozu_pattern(data: pd.DataFrame) -> float:
        """
        Identify Marubozu pattern (strong candle, no wicks).
        
        Returns Marubozu signal 0-100.
        """
        if len(data) < 1:
            return 50.0

        open_price = data['Open'].values[-1]
        close_price = data['Close'].values[-1]
        high = data['High'].values[-1]
        low = data['Low'].values[-1]

        # Marubozu: open and close at extremes, no or tiny wicks
        if (open_price == low and close_price == high) or \
           (close_price == low and open_price == high):
            return 85.0

        body = abs(close_price - open_price)
        total_range = high - low

        if total_range > 0 and body > total_range * 0.95:
            return 75.0
        else:
            return 50.0
