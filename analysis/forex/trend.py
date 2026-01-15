"""Trend analysis for Forex."""

import numpy as np
import pandas as pd
from analysis.shared.indicators import TechnicalIndicators


class TrendAnalysis:
    """Analyzes Forex trends."""

    @staticmethod
    def moving_average_crossover(data: pd.DataFrame) -> float:
        """
        Analyze moving average crossover signals.
        
        Returns trend signal 0-100.
        """
        if len(data) < 50:
            return 50.0

        closes = data['Close'].values
        sma20 = TechnicalIndicators.sma(closes, 20)
        sma50 = TechnicalIndicators.sma(closes, 50)

        if sma20[-1] > sma50[-1]:
            return 75.0
        elif sma20[-1] < sma50[-1]:
            return 25.0
        else:
            return 50.0

    @staticmethod
    def ema_trend(data: pd.DataFrame) -> float:
        """
        Analyze exponential moving average trend.
        
        Returns trend strength 0-100.
        """
        if len(data) < 200:
            return 50.0

        closes = data['Close'].values
        ema12 = TechnicalIndicators.ema(closes, 12)
        ema26 = TechnicalIndicators.ema(closes, 26)
        ema200 = TechnicalIndicators.ema(closes, 200)

        current = closes[-1]
        signal = 50.0

        if current > ema12[-1] > ema26[-1] > ema200[-1]:
            signal = 90.0
        elif current < ema12[-1] < ema26[-1] < ema200[-1]:
            signal = 10.0
        elif ema12[-1] > ema26[-1]:
            signal = 70.0
        elif ema12[-1] < ema26[-1]:
            signal = 30.0

        return signal

    @staticmethod
    def adx_trend_strength(data: pd.DataFrame) -> float:
        """
        Analyze ADX for trend strength.
        
        Returns trend strength score 0-100.
        """
        if len(data) < 30:
            return 50.0

        highs = data['High'].values
        lows = data['Low'].values
        closes = data['Close'].values

        adx = TechnicalIndicators.adx(highs, lows, closes, period=14)

        current_adx = adx[-1]
        if np.isnan(current_adx):
            return 50.0

        # Scale ADX (typically 0-100) to signal strength
        return min(current_adx, 100.0)

    @staticmethod
    def price_slope(data: pd.DataFrame, period: int = 20) -> float:
        """
        Analyze price slope for trend momentum.
        
        Returns slope strength -100 to 100 (normalized to 0-100).
        """
        if len(data) < period:
            return 50.0

        closes = data['Close'].values[-period:]
        x = np.arange(len(closes))

        # Linear regression slope
        slope = np.polyfit(x, closes, 1)[0]
        normalized_slope = slope / (np.mean(closes) / 100)

        # Convert to 0-100 scale
        signal = 50.0 + np.clip(normalized_slope * 5, -50, 50)
        return signal

    @staticmethod
    def supertrend_indicator(data: pd.DataFrame) -> float:
        """
        Calculate Supertrend indicator signal.
        
        Returns supertrend signal 0-100.
        """
        if len(data) < 10:
            return 50.0

        highs = data['High'].values
        lows = data['Low'].values
        closes = data['Close'].values

        period = 10
        multiplier = 3.0

        # Calculate basic bands
        hl2 = (highs + lows) / 2
        atr_vals = np.zeros_like(closes)
        atr_vals[0] = highs[0] - lows[0]

        for i in range(1, len(closes)):
            tr = max(highs[i] - lows[i], abs(highs[i] - closes[i-1]), abs(lows[i] - closes[i-1]))
            atr_vals[i] = (atr_vals[i-1] * (period - 1) + tr) / period

        # Basic bands
        final_lb = hl2 - multiplier * atr_vals
        final_ub = hl2 + multiplier * atr_vals

        # Determine trend
        if closes[-1] > final_ub[-1]:
            return 80.0
        elif closes[-1] < final_lb[-1]:
            return 20.0
        else:
            return 50.0

    @staticmethod
    def vwap_trend(data: pd.DataFrame) -> float:
        """
        Analyze price position relative to VWAP.
        
        Returns VWAP signal 0-100.
        """
        if len(data) < 20:
            return 50.0

        high = data['High'].values
        low = data['Low'].values
        close = data['Close'].values
        volume = data['Volume'].values

        # Calculate VWAP
        typical_price = (high + low + close) / 3
        vwap = np.cumsum(typical_price * volume) / np.cumsum(volume)

        current_price = close[-1]
        current_vwap = vwap[-1]

        if current_price > current_vwap:
            diff = (current_price - current_vwap) / current_vwap * 100
            return 50.0 + min(diff * 10, 50.0)
        else:
            diff = (current_vwap - current_price) / current_vwap * 100
            return 50.0 - min(diff * 10, 50.0)

    @staticmethod
    def rsi_trend(data: pd.DataFrame) -> float:
        """
        Analyze trend using RSI.
        
        Returns RSI-based trend signal 0-100.
        """
        if len(data) < 20:
            return 50.0

        closes = data['Close'].values
        rsi = TechnicalIndicators.rsi(closes, period=14)

        current_rsi = rsi[-1]
        if np.isnan(current_rsi):
            return 50.0

        return current_rsi  # Already 0-100 scale

    @staticmethod
    def macd_trend(data: pd.DataFrame) -> float:
        """
        Analyze trend using MACD.
        
        Returns MACD-based trend signal 0-100.
        """
        if len(data) < 30:
            return 50.0

        closes = data['Close'].values
        macd_line, signal_line, histogram = TechnicalIndicators.macd(closes)

        if histogram[-1] > histogram[-2] > 0:
            return 75.0
        elif histogram[-1] < histogram[-2] < 0:
            return 25.0
        elif histogram[-1] > 0:
            return 65.0
        elif histogram[-1] < 0:
            return 35.0
        else:
            return 50.0

    @staticmethod
    def trend_strength_confirmation(data: pd.DataFrame) -> float:
        """Compatibility shim: historical name used by general analyzer.

        Delegate to `adx_trend_strength` for a simple trend strength estimate.
        """
        return TrendAnalysis.adx_trend_strength(data)
