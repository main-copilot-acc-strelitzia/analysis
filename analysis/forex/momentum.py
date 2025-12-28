"""Momentum analysis for Forex."""

import numpy as np
import pandas as pd
from analysis.shared.indicators import TechnicalIndicators
from analysis.shared.statistics import StatisticalTools


class MomentumAnalysis:
    """Analyzes Forex momentum."""

    @staticmethod
    def rsi_momentum(data: pd.DataFrame) -> float:
        """
        Measure momentum using RSI.
        
        Returns momentum signal 0-100.
        """
        if len(data) < 20:
            return 50.0

        closes = data['Close'].values
        rsi = TechnicalIndicators.rsi(closes, period=14)

        current_rsi = rsi[-1]
        if np.isnan(current_rsi):
            return 50.0

        if current_rsi > 70:
            return 85.0
        elif current_rsi < 30:
            return 15.0
        else:
            return current_rsi

    @staticmethod
    def stochastic_momentum(data: pd.DataFrame) -> float:
        """
        Measure momentum using Stochastic Oscillator.
        
        Returns momentum signal 0-100.
        """
        if len(data) < 20:
            return 50.0

        highs = data['High'].values
        lows = data['Low'].values
        closes = data['Close'].values

        k_vals, d_vals = TechnicalIndicators.stochastic(highs, lows, closes, period=14)

        k_current = k_vals[-1]
        if np.isnan(k_current):
            return 50.0

        if k_current > 80:
            return 80.0
        elif k_current < 20:
            return 20.0
        else:
            return k_current

    @staticmethod
    def roc_momentum(data: pd.DataFrame) -> float:
        """
        Measure momentum using Rate of Change.
        
        Returns momentum signal 0-100 (normalized).
        """
        if len(data) < 15:
            return 50.0

        closes = data['Close'].values
        roc = TechnicalIndicators.roc(closes, period=12)

        current_roc = roc[-1]
        if np.isnan(current_roc) or np.isinf(current_roc):
            return 50.0

        # Normalize ROC to 0-100 range
        signal = 50.0 + np.clip(current_roc / 2, -50, 50)
        return signal

    @staticmethod
    def price_momentum(data: pd.DataFrame, period: int = 10) -> float:
        """
        Calculate price momentum over period.
        
        Returns momentum strength 0-100.
        """
        if len(data) < period:
            return 50.0

        closes = data['Close'].values
        returns = StatisticalTools.calculate_returns(closes[-period:])

        if len(returns) == 0:
            return 50.0

        momentum = np.sum(returns) * 100
        signal = 50.0 + np.clip(momentum * 50, -50, 50)
        return signal

    @staticmethod
    def williams_r_momentum(data: pd.DataFrame) -> float:
        """
        Measure momentum using Williams %R.
        
        Returns momentum signal 0-100.
        """
        if len(data) < 20:
            return 50.0

        highs = data['High'].values
        lows = data['Low'].values
        closes = data['Close'].values

        wr = TechnicalIndicators.williams_percent_r(highs, lows, closes, period=14)

        current_wr = wr[-1]
        if np.isnan(current_wr):
            return 50.0

        # Convert -100 to 0 range to 0-100
        return 100.0 + current_wr

    @staticmethod
    def cci_momentum(data: pd.DataFrame) -> float:
        """
        Measure momentum using CCI.
        
        Returns momentum signal 0-100 (normalized).
        """
        if len(data) < 25:
            return 50.0

        highs = data['High'].values
        lows = data['Low'].values
        closes = data['Close'].values

        cci = TechnicalIndicators.cci(highs, lows, closes, period=20)

        current_cci = cci[-1]
        if np.isnan(current_cci):
            return 50.0

        # CCI typically -100 to +100
        signal = 50.0 + np.clip(current_cci / 2, -50, 50)
        return signal

    @staticmethod
    def volume_momentum(data: pd.DataFrame) -> float:
        """
        Analyze momentum based on volume.
        
        Returns volume momentum 0-100.
        """
        if len(data) < 10:
            return 50.0

        volumes = data['Volume'].values[-10:]
        closes = data['Close'].values[-10:]

        avg_volume = np.mean(volumes)
        current_volume = volumes[-1]
        recent_change = closes[-1] - closes[-5]

        # High volume with positive price move
        if current_volume > avg_volume * 1.2 and recent_change > 0:
            return 80.0
        elif current_volume > avg_volume * 1.2 and recent_change < 0:
            return 20.0
        elif current_volume < avg_volume * 0.8:
            return 50.0
        else:
            return 50.0

    @staticmethod
    def obv_momentum(data: pd.DataFrame) -> float:
        """
        Analyze momentum using On-Balance Volume.
        
        Returns OBV momentum signal 0-100.
        """
        if len(data) < 20:
            return 50.0

        closes = data['Close'].values
        volumes = data['Volume'].values

        obv = TechnicalIndicators.obv(closes, volumes)

        if obv[-1] > obv[-10]:
            diff = (obv[-1] - obv[-10]) / abs(obv[-10]) * 100 if obv[-10] != 0 else 0
            return min(50.0 + (diff / 2), 100.0)
        else:
            diff = (obv[-10] - obv[-1]) / abs(obv[-10]) * 100 if obv[-10] != 0 else 0
            return max(50.0 - (diff / 2), 0.0)
