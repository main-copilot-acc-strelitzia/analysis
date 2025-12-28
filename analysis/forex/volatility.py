"""Volatility analysis for Forex."""

import numpy as np
import pandas as pd
from analysis.shared.indicators import TechnicalIndicators
from analysis.shared.statistics import StatisticalTools


class VolatilityAnalysis:
    """Analyzes Forex volatility."""

    @staticmethod
    def atr_volatility(data: pd.DataFrame) -> float:
        """
        Measure volatility using ATR.
        
        Returns volatility level 0-100 (normalized).
        """
        if len(data) < 20:
            return 50.0

        highs = data['High'].values
        lows = data['Low'].values
        closes = data['Close'].values

        atr = TechnicalIndicators.atr(highs, lows, closes, period=14)
        current_atr = atr[-1]
        avg_atr = np.mean(atr[-20:])

        if avg_atr == 0:
            return 50.0

        ratio = current_atr / avg_atr
        signal = 50.0 + (ratio - 1.0) * 50
        return np.clip(signal, 0, 100.0)

    @staticmethod
    def bollinger_band_squeeze(data: pd.DataFrame) -> float:
        """
        Detect Bollinger Band squeeze.
        
        Returns squeeze signal 0-100 (0=tight, 100=wide).
        """
        if len(data) < 25:
            return 50.0

        closes = data['Close'].values
        upper, middle, lower = TechnicalIndicators.bollinger_bands(closes, period=20)

        current_width = upper[-1] - lower[-1]
        avg_width = np.mean(upper[-20:] - lower[-20:])

        if avg_width == 0:
            return 50.0

        ratio = current_width / avg_width
        return np.clip(ratio * 50, 0, 100.0)

    @staticmethod
    def historical_volatility(data: pd.DataFrame) -> float:
        """
        Calculate historical volatility.
        
        Returns volatility score 0-100.
        """
        if len(data) < 20:
            return 50.0

        closes = data['Close'].values
        returns = StatisticalTools.calculate_returns(closes)

        volatility = StatisticalTools.volatility(returns, periods=252)

        # Normalize volatility (typical forex 0.5% - 5%)
        signal = min(volatility * 500, 100.0)
        return signal

    @staticmethod
    def volatility_clustering(data: pd.DataFrame, period: int = 20) -> float:
        """
        Detect volatility clustering patterns.
        
        Returns clustering strength 0-100.
        """
        if len(data) < period:
            return 50.0

        closes = data['Close'].values
        returns = StatisticalTools.calculate_returns(closes)

        # Split into periods
        recent_vol = np.std(returns[-10:])
        prior_vol = np.std(returns[-20:-10])

        if prior_vol == 0:
            return 50.0

        ratio = recent_vol / prior_vol
        if ratio > 1.2:
            return 75.0
        elif ratio < 0.8:
            return 25.0
        else:
            return 50.0

    @staticmethod
    def average_true_range_percent(data: pd.DataFrame) -> float:
        """
        Calculate ATR as percentage of price.
        
        Returns ATR% signal 0-100.
        """
        if len(data) < 20:
            return 50.0

        highs = data['High'].values
        lows = data['Low'].values
        closes = data['Close'].values

        atr = TechnicalIndicators.atr(highs, lows, closes, period=14)

        current_atr_pct = (atr[-1] / closes[-1]) * 100

        # Typical ATR% is 0.5 - 2%
        signal = min(current_atr_pct * 50, 100.0)
        return signal

    @staticmethod
    def range_volatility(data: pd.DataFrame, period: int = 20) -> float:
        """
        Measure volatility based on price range.
        
        Returns range volatility 0-100.
        """
        if len(data) < period:
            return 50.0

        highs = data['High'].values[-period:]
        lows = data['Low'].values[-period:]
        closes = data['Close'].values[-period:]

        ranges = highs - lows
        avg_range = np.mean(ranges)
        current_range = ranges[-1]

        if avg_range == 0:
            return 50.0

        ratio = current_range / avg_range
        return np.clip(ratio * 50, 0, 100.0)

    @staticmethod
    def parkinson_volatility(data: pd.DataFrame, period: int = 20) -> float:
        """
        Calculate Parkinson volatility (range-based).
        
        Returns volatility score 0-100.
        """
        if len(data) < period:
            return 50.0

        highs = data['High'].values[-period:]
        lows = data['Low'].values[-period:]

        log_ratio = np.log(highs / lows)
        parkinson_vol = np.sqrt(np.mean(log_ratio ** 2) / (4 * np.log(2)))

        # Normalize (typical 0.5% - 3%)
        signal = min(parkinson_vol * 1500, 100.0)
        return signal

    @staticmethod
    def keltner_channel_width(data: pd.DataFrame) -> float:
        """
        Measure Keltner Channel width.
        
        Returns channel width signal 0-100.
        """
        if len(data) < 25:
            return 50.0

        highs = data['High'].values
        lows = data['Low'].values
        closes = data['Close'].values

        # Keltner Channel = EMA +/- (ATR)
        atr = TechnicalIndicators.atr(highs, lows, closes, period=10)
        ema = TechnicalIndicators.ema(closes, 20)

        upper = ema + (atr * 2)
        lower = ema - (atr * 2)

        current_width = upper[-1] - lower[-1]
        avg_width = np.mean(upper[-10:] - lower[-10:])

        if avg_width == 0:
            return 50.0

        ratio = current_width / avg_width
        return np.clip(ratio * 50, 0, 100.0)
